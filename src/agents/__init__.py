"""LangChain agents for CI/CD failure analysis"""
from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from src.config import settings
from src.utils.logger import get_logger
from src.rag import RAGPipeline, ChromaDBManager
from src.utils.parser import parse_ci_cd_logs, extract_error_context

logger = get_logger(__name__)


class RCAgent:
    """Root Cause Analysis Agent using LangChain"""
    
    def __init__(self, rag_pipeline: RAGPipeline = None):
        """
        Initialize RCA Agent.
        
        Args:
            rag_pipeline: Optional RAG pipeline for documentation retrieval
        """
        # Only initialize ChatOpenAI if API key is available
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                model_name=settings.llm_model,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.llm = None
        
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.logger = logger
    
    def analyze_failure(self, log_content: str, query: str = None) -> Dict[str, Any]:
        """
        Analyze CI/CD failure logs and provide RCA.
        
        Args:
            log_content: Raw CI/CD log content
            query: Optional specific query about the failure
            
        Returns:
            Dictionary containing RCA analysis
        """
        self.logger.info("Starting failure analysis")
        
        # Parse logs
        log_entries = parse_ci_cd_logs(log_content)
        error_context = extract_error_context(log_content)
        
        # Retrieve relevant documentation
        docs = self.rag_pipeline.retrieve_relevant_docs(
            error_context or "CI/CD test failure",
            top_k=settings.top_k_retrieval
        )
        
        # Prepare messages for LLM
        system_prompt = self._get_rca_system_prompt(docs)
        user_message = self._prepare_analysis_request(log_content, log_entries, query)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Call LLM
        response = self.llm(messages)
        
        # Parse response
        analysis = self._parse_rca_response(response.content)
        
        self.logger.info("Failure analysis completed")
        
        return analysis
    
    def _get_rca_system_prompt(self, relevant_docs: List[str]) -> str:
        """Generate system prompt with context"""
        docs_context = "\n\n".join(relevant_docs[:3]) if relevant_docs else "No relevant documentation found."
        
        return f"""You are an expert CI/CD failure diagnostician. Your task is to analyze CI/CD pipeline failure logs and provide comprehensive Root Cause Analysis (RCA).

Analyze the provided logs systematically to identify:
1. Root causes of the failure
2. Failure chain (sequence of events leading to failure)
3. Affected components
4. Severity and impact assessment

RELEVANT DOCUMENTATION:
{docs_context}

Provide your analysis in JSON format with the following structure:
{{
    "root_causes": ["cause1", "cause2"],
    "failure_chain": ["step1", "step2"],
    "affected_components": ["component1", "component2"],
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "impact": "description of impact",
    "confidence_score": 0.85,
    "summary": "brief summary"
}}"""
    
    def _prepare_analysis_request(self, log_content: str, log_entries: List, query: Optional[str]) -> str:
        """Prepare the analysis request message"""
        base_message = f"""Analyze the following CI/CD failure logs:

LOGS:
{log_content[:5000]}  # Limit to first 5000 chars

PARSED ENTRIES:
{len(log_entries)} log entries found

ERROR CONTEXT:
{extract_error_context(log_content)}"""
        
        if query:
            base_message += f"\n\nFOCUS AREA: {query}"
        
        return base_message
    
    def _parse_rca_response(self, response_text: str) -> Dict[str, Any]:
        """Parse RCA response from LLM"""
        import json
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.warning(f"Failed to parse structured response: {e}")
        
        # Return parsed text response
        return {
            "root_causes": ["See analysis below"],
            "failure_chain": [],
            "affected_components": [],
            "severity": "UNKNOWN",
            "impact": response_text,
            "confidence_score": 0.5,
            "summary": response_text[:200]
        }


class RemediationAgent:
    """Remediation suggestion agent"""
    
    def __init__(self, rag_pipeline: RAGPipeline = None):
        """
        Initialize Remediation Agent.
        
        Args:
            rag_pipeline: Optional RAG pipeline for documentation retrieval
        """
        # Only initialize ChatOpenAI if API key is available
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                temperature=settings.temperature - 0.2,  # Lower temp for more focused suggestions
                max_tokens=settings.max_tokens,
                model_name=settings.llm_model,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.llm = None
        
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.logger = logger
    
    def generate_suggestions(self, rca_analysis: Dict[str, Any], log_content: str) -> List[Dict[str, Any]]:
        """
        Generate remediation suggestions based on RCA analysis.
        
        Args:
            rca_analysis: RCA analysis result
            log_content: Original log content
            
        Returns:
            List of remediation suggestions
        """
        self.logger.info("Generating remediation suggestions")
        
        # Retrieve resolution documentation
        root_causes_text = " ".join(rca_analysis.get("root_causes", []))
        docs = self.rag_pipeline.retrieve_relevant_docs(
            f"fix solution {root_causes_text}",
            top_k=settings.top_k_retrieval
        )
        
        # Prepare prompt
        system_prompt = self._get_remediation_system_prompt(docs)
        user_message = self._prepare_suggestion_request(rca_analysis, log_content)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Call LLM
        response = self.llm(messages)
        
        # Parse suggestions
        suggestions = self._parse_suggestions_response(response.content)
        
        self.logger.info(f"Generated {len(suggestions)} remediation suggestions")
        
        return suggestions
    
    def _get_remediation_system_prompt(self, relevant_docs: List[str]) -> str:
        """Generate remediation system prompt"""
        docs_context = "\n\n".join(relevant_docs[:3]) if relevant_docs else "No relevant documentation found."
        
        return f"""You are an expert DevOps engineer providing remediation guidance for CI/CD failures.

Provide practical, actionable remediation suggestions with:
1. Priority level (CRITICAL, HIGH, MEDIUM, LOW)
2. Specific action steps
3. Estimated time to fix
4. Risk level assessment
5. Probability of success

RELEVANT SOLUTIONS DOCUMENTATION:
{docs_context}

Return suggestions as a JSON array:
[
    {{
        "action": "specific action",
        "priority": "CRITICAL|HIGH|MEDIUM|LOW",
        "estimated_fix_time": "15 minutes",
        "risk_level": "LOW|MEDIUM|HIGH",
        "success_probability": 0.95,
        "steps": ["step1", "step2"],
        "details": "detailed explanation",
        "related_docs": ["doc1", "doc2"]
    }}
]"""
    
    def _prepare_suggestion_request(self, rca_analysis: Dict[str, Any], log_content: str) -> str:
        """Prepare suggestion request message"""
        return f"""Based on the following RCA analysis, provide remediation suggestions:

ROOT CAUSES:
{', '.join(rca_analysis.get('root_causes', []))}

SEVERITY: {rca_analysis.get('severity', 'UNKNOWN')}
AFFECTED COMPONENTS: {', '.join(rca_analysis.get('affected_components', []))}

SUMMARY: {rca_analysis.get('summary', 'N/A')}

Considering these root causes and the failure context, provide the most effective remediation strategies."""
    
    def _parse_suggestions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse remediation suggestions from response"""
        import json
        import re
        
        try:
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.warning(f"Failed to parse suggestions: {e}")
        
        # Return default suggestion if parsing fails
        return [{
            "action": response_text[:100],
            "priority": "MEDIUM",
            "estimated_fix_time": "30 minutes",
            "risk_level": "MEDIUM",
            "success_probability": 0.7,
            "steps": [response_text],
            "details": "See analysis above for details",
            "related_docs": []
        }]


class CIDDQAAgent:
    """Main orchestrator agent for CI/CD QA"""
    
    def __init__(self, rag_pipeline: RAGPipeline = None):
        """
        Initialize CI/CD QA Agent.
        
        Args:
            rag_pipeline: Optional RAG pipeline
        """
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.rca_agent = RCAgent(self.rag_pipeline)
        self.remediation_agent = RemediationAgent(self.rag_pipeline)
        self.logger = logger
    
    def analyze_and_remediate(self, log_content: str, query: str = None) -> Dict[str, Any]:
        """
        Complete analysis and remediation workflow.
        
        Args:
            log_content: CI/CD failure logs
            query: Optional specific query
            
        Returns:
            Complete analysis with RCA and remediation suggestions
        """
        self.logger.info("Starting CI/CD analysis workflow")
        
        # Step 1: RCA
        rca_analysis = self.rca_agent.analyze_failure(log_content, query)
        
        # Step 2: Generate remediation suggestions
        remediation_suggestions = self.remediation_agent.generate_suggestions(
            rca_analysis, log_content
        )
        
        # Combine results
        result = {
            "status": "completed",
            "rca": rca_analysis,
            "remediation_suggestions": remediation_suggestions,
            "rag_stats": self.rag_pipeline.get_stats()
        }
        
        self.logger.info("CI/CD analysis workflow completed")
        
        return result
