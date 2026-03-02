"""Output formatting utilities"""
from typing import List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class RemediationSuggestion:
    """Remediation suggestion structure"""
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    action: str
    estimated_fix_time: str
    risk_level: str
    success_probability: float


def format_remediation_suggestions(suggestions: List[Dict[str, Any]]) -> str:
    """
    Format remediation suggestions into readable output.
    
    Args:
        suggestions: List of suggestion dictionaries
        
    Returns:
        Formatted string of recommendations
    """
    if not suggestions:
        return "No remediation suggestions available."
    
    output = "📋 **REMEDIATION SUGGESTIONS**\n"
    output += "=" * 60 + "\n\n"
    
    for idx, suggestion in enumerate(suggestions, 1):
        priority = suggestion.get('priority', 'UNKNOWN')
        icon = get_priority_icon(priority)
        
        output += f"{icon} **Suggestion {idx}: {suggestion.get('action', 'Unknown')}\n"
        output += f"   Priority: {priority}\n"
        output += f"   Estimated Fix Time: {suggestion.get('estimated_fix_time', 'Unknown')}\n"
        output += f"   Risk Level: {suggestion.get('risk_level', 'Unknown')}\n"
        output += f"   Success Probability: {suggestion.get('success_probability', 0):.1%}\n"
        
        if 'details' in suggestion:
            output += f"   Details: {suggestion['details']}\n"
        
        if 'steps' in suggestion:
            output += "   Steps:\n"
            for step_idx, step in enumerate(suggestion['steps'], 1):
                output += f"      {step_idx}. {step}\n"
        
        if 'related_docs' in suggestion:
            output += f"   Related Documentation: {', '.join(suggestion['related_docs'])}\n"
        
        output += "\n"
    
    return output


def get_priority_icon(priority: str) -> str:
    """Get icon for priority level"""
    icons = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    return icons.get(priority.upper(), '⚪')


def format_rca_analysis(analysis: Dict[str, Any]) -> str:
    """
    Format RCA analysis into readable output.
    
    Args:
        analysis: RCA analysis dictionary
        
    Returns:
        Formatted string of the analysis
    """
    output = "🔍 **ROOT CAUSE ANALYSIS**\n"
    output += "=" * 60 + "\n\n"
    
    if 'root_causes' in analysis:
        output += "**Root Causes:**\n"
        for cause in analysis['root_causes']:
            output += f"  • {cause}\n"
        output += "\n"
    
    if 'failure_chain' in analysis:
        output += "**Failure Chain:**\n"
        for idx, event in enumerate(analysis['failure_chain'], 1):
            output += f"  {idx}. {event}\n"
        output += "\n"
    
    if 'affected_components' in analysis:
        output += "**Affected Components:**\n"
        for component in analysis['affected_components']:
            output += f"  • {component}\n"
        output += "\n"
    
    if 'confidence_score' in analysis:
        output += f"**Confidence Score:** {analysis['confidence_score']:.1%}\n\n"
    
    return output


def format_as_json(data: Any) -> str:
    """Format data as pretty JSON"""
    return json.dumps(data, indent=2, default=str)
