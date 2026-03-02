"""CI/CD Log parser utility"""
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class LogLevel(str, Enum):
    """Log level enumeration"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


@dataclass
class LogEntry:
    """Structured log entry from CI/CD pipeline"""
    timestamp: datetime
    level: LogLevel
    component: str
    message: str
    stack_trace: Optional[str] = None
    raw_log: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "stack_trace": self.stack_trace,
        }


def parse_ci_cd_logs(log_content: str) -> List[LogEntry]:
    """
    Parse CI/CD logs and extract structured entries.
    
    Supports common formats like:
    - [TIMESTAMP] [LEVEL] [COMPONENT] Message
    - JSON logs
    """
    entries = []
    
    # Try JSON format first
    try:
        log_lines = log_content.strip().split('\n')
        for line in log_lines:
            if line.strip():
                try:
                    json_log = json.loads(line)
                    entry = LogEntry(
                        timestamp=datetime.fromisoformat(json_log.get('timestamp', datetime.now().isoformat())),
                        level=LogLevel(json_log.get('level', 'INFO').upper()),
                        component=json_log.get('component', 'unknown'),
                        message=json_log.get('message', line),
                        stack_trace=json_log.get('stack_trace'),
                        raw_log=line
                    )
                    entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        if entries:
            return entries
    except Exception:
        pass
    
    # Fallback to text format parsing
    # Pattern: [TIMESTAMP] [LEVEL] [COMPONENT] Message
    pattern = r'\[(.+?)\]\s+\[(\w+)\]\s+\[(\w+)\]\s+(.*?)(?=\n\[|$)'
    matches = re.finditer(pattern, log_content, re.DOTALL)
    
    for match in matches:
        timestamp_str, level, component, message = match.groups()
        
        # Extract stack trace if present
        stack_trace = None
        if 'Traceback' in message or 'Error' in message:
            lines = message.split('\n')
            stack_trace = '\n'.join(lines[1:]).strip()
            message = lines[0].strip()
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            timestamp = datetime.now()
        
        entry = LogEntry(
            timestamp=timestamp,
            level=LogLevel(level.upper()),
            component=component.lower(),
            message=message.strip(),
            stack_trace=stack_trace,
            raw_log=match.group(0)
        )
        entries.append(entry)
    
    # If no pattern matched, create a single entry from the entire content
    if not entries:
        entries.append(LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            component="pipeline",
            message=log_content[:500],
            stack_trace=log_content if len(log_content) > 500 else None,
            raw_log=log_content
        ))
    
    return entries


def extract_error_context(log_content: str, max_lines: int = 10) -> str:
    """Extract relevant error context from logs"""
    lines = log_content.split('\n')
    error_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword in line.upper() for keyword in ['ERROR', 'FAILED', 'EXCEPTION', 'TRACEBACK']):
            # Include surrounding context
            start = max(0, i - 2)
            end = min(len(lines), i + max_lines)
            error_lines.extend(lines[start:end])
            break
    
    return '\n'.join(error_lines) if error_lines else log_content[:1000]
