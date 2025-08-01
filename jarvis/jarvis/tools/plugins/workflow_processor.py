"""
Natural Language Workflow Processor for Full-Stack Development
"""
from typing import Dict, List
import json
import re

class WorkflowProcessor:
    def __init__(self):
        self.current_phase = None
        self.project_context = {}
        
    def process_request(self, user_request: str) -> Dict:
        """
        Process a natural language request and determine the appropriate workflow phase
        """
        # Normalize request
        request = user_request.lower().strip()
        
        # Identify phase from request
        phase = self._identify_phase(request)
        action = self._identify_action(request)
        
        return {
            "phase": phase,
            "action": action,
            "context": self._extract_context(request),
            "next_steps": self._get_next_steps(phase, action)
        }
    
    def _identify_phase(self, request: str) -> str:
        """
        Identify which development phase the request relates to
        """
        phase_keywords = {
            "research": ["research", "best practices", "learn", "study", "investigate"],
            "initialization": ["start", "setup", "init", "create project", "new project"],
            "frontend": ["frontend", "ui", "interface", "component", "react", "vue", "angular"],
            "backend": ["backend", "api", "server", "endpoint", "service"],
            "database": ["database", "data", "storage", "model", "schema"],
            "testing": ["test", "verify", "validate", "check"],
            "deployment": ["deploy", "publish", "release", "host"]
        }
        
        for phase, keywords in phase_keywords.items():
            if any(keyword in request for keyword in keywords):
                return phase
                
        return "initialization"  # default phase
    
    def _identify_action(self, request: str) -> str:
        """
        Identify the specific action needed within a phase
        """
        action_keywords = {
            "create": ["create", "make", "build", "new"],
            "update": ["update", "modify", "change", "improve"],
            "delete": ["delete", "remove", "eliminate"],
            "view": ["view", "show", "display", "list"],
            "test": ["test", "verify", "validate"],
            "deploy": ["deploy", "publish", "release"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in request for keyword in keywords):
                return action
                
        return "create"  # default action
    
    def _extract_context(self, request: str) -> Dict:
        """
        Extract relevant context from the request
        """
        context = {
            "tech_stack": self._extract_tech_stack(request),
            "features": self._extract_features(request),
            "constraints": self._extract_constraints(request)
        }
        return context
    
    def _extract_tech_stack(self, request: str) -> Dict:
        """
        Extract technology stack preferences from request
        """
        tech_patterns = {
            "frontend": r"(react|vue|angular|svelte)",
            "backend": r"(node|python|java|go)",
            "database": r"(mongodb|postgres|mysql|sqlite)"
        }
        
        tech_stack = {}
        for tech_type, pattern in tech_patterns.items():
            matches = re.findall(pattern, request)
            if matches:
                tech_stack[tech_type] = matches[0]
                
        return tech_stack
    
    def _extract_features(self, request: str) -> List[str]:
        """
        Extract requested features from the request
        """
        feature_patterns = [
            r"with ([a-z\s]+) functionality",
            r"including ([a-z\s]+)",
            r"that has ([a-z\s]+)"
        ]
        
        features = []
        for pattern in feature_patterns:
            matches = re.findall(pattern, request)
            features.extend(matches)
            
        return features
    
    def _extract_constraints(self, request: str) -> List[str]:
        """
        Extract any constraints or requirements
        """
        constraint_patterns = [
            r"must have ([a-z\s]+)",
            r"requires ([a-z\s]+)",
            r"needs ([a-z\s]+)"
        ]
        
        constraints = []
        for pattern in constraint_patterns:
            matches = re.findall(pattern, request)
            constraints.extend(matches)
            
        return constraints
    
    def _get_next_steps(self, phase: str, action: str) -> List[str]:
        """
        Generate next steps based on the identified phase and action
        """
        # Load workflow guide steps
        with open("fullstack_workflow_guide.md", "r") as f:
            workflow = f.read()
            
        # Extract relevant section based on phase
        phase_pattern = rf"## \d+\. {phase.title()}.*?(?=## \d+\.|$)"
        phase_content = re.findall(phase_pattern, workflow, re.DOTALL | re.IGNORECASE)
        
        if not phase_content:
            return ["Please refer to the workflow guide for detailed steps"]
            
        # Extract bullet points as steps
        steps = re.findall(r"- (.*?)(?=\n|$)", phase_content[0])
        return steps if steps else ["No specific steps found for this phase"]
