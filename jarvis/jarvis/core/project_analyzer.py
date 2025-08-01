"""
Project Requirements Analyzer

Analyzes project descriptions and requirements to determine optimal
development approach, tech stack, and implementation strategy.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .workflow_standards import ProfessionalWorkflowStandards


@dataclass
class ProjectAnalysis:
    """Results of project requirements analysis."""
    project_type: str
    complexity_level: str  # "simple", "moderate", "complex"
    recommended_tech_stack: Dict[str, str]
    estimated_timeline: str
    key_features: List[str]
    technical_challenges: List[str]
    security_requirements: List[str]
    performance_requirements: List[str]
    deployment_considerations: List[str]


class ProjectRequirementsAnalyzer:
    """
    Analyzes project descriptions to extract requirements and recommend
    optimal development approaches.
    """
    
    def __init__(self):
        self.workflow_standards = ProfessionalWorkflowStandards()
        self.project_patterns = self._initialize_project_patterns()
        self.tech_stack_recommendations = self.workflow_standards.get_tech_stack_recommendations()
    
    def analyze_project(self, project_description: str, additional_requirements: str = "") -> ProjectAnalysis:
        """
        Analyze project description and requirements to determine optimal approach.
        
        Args:
            project_description: Main description of what to build
            additional_requirements: Additional specific requirements
            
        Returns:
            ProjectAnalysis with recommendations and assessments
        """
        combined_text = f"{project_description} {additional_requirements}".lower()
        
        # Determine project type
        project_type = self._determine_project_type(combined_text)
        
        # Assess complexity
        complexity_level = self._assess_complexity(combined_text)
        
        # Extract key features
        key_features = self._extract_key_features(combined_text)
        
        # Recommend tech stack
        recommended_tech_stack = self._recommend_tech_stack(project_type, key_features, complexity_level)
        
        # Identify technical challenges
        technical_challenges = self._identify_technical_challenges(combined_text, project_type)
        
        # Determine security requirements
        security_requirements = self._determine_security_requirements(combined_text, project_type)
        
        # Assess performance requirements
        performance_requirements = self._assess_performance_requirements(combined_text, complexity_level)
        
        # Consider deployment needs
        deployment_considerations = self._assess_deployment_needs(combined_text, complexity_level)
        
        # Estimate timeline
        estimated_timeline = self._estimate_timeline(complexity_level, len(key_features))
        
        return ProjectAnalysis(
            project_type=project_type,
            complexity_level=complexity_level,
            recommended_tech_stack=recommended_tech_stack,
            estimated_timeline=estimated_timeline,
            key_features=key_features,
            technical_challenges=technical_challenges,
            security_requirements=security_requirements,
            performance_requirements=performance_requirements,
            deployment_considerations=deployment_considerations
        )
    
    def _initialize_project_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for project type detection."""
        return {
            "web_application": [
                "web app", "website", "web application", "dashboard", "portal",
                "management system", "admin panel", "user interface"
            ],
            "api_service": [
                "api", "service", "microservice", "backend", "rest api",
                "graphql", "web service", "data service"
            ],
            "real_time_app": [
                "chat", "messaging", "real-time", "live", "websocket",
                "notification", "streaming", "collaborative"
            ],
            "data_dashboard": [
                "dashboard", "analytics", "reporting", "visualization",
                "metrics", "charts", "graphs", "business intelligence"
            ],
            "e_commerce": [
                "shop", "store", "e-commerce", "ecommerce", "marketplace",
                "cart", "payment", "checkout", "product catalog"
            ],
            "social_platform": [
                "social", "community", "forum", "blog", "social network",
                "user profiles", "posts", "comments", "likes"
            ],
            "task_management": [
                "task", "todo", "project management", "kanban", "workflow",
                "assignment", "tracking", "productivity"
            ]
        }
    
    def _determine_project_type(self, text: str) -> str:
        """Determine the primary project type based on description."""
        scores = {}
        
        for project_type, patterns in self.project_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                scores[project_type] = score
        
        if not scores:
            return "web_application"  # Default fallback
        
        return max(scores, key=scores.get)
    
    def _assess_complexity(self, text: str) -> str:
        """Assess project complexity based on features and requirements."""
        complexity_indicators = {
            "simple": [
                "simple", "basic", "minimal", "straightforward", "easy"
            ],
            "moderate": [
                "user authentication", "database", "api", "responsive",
                "search", "filtering", "notifications"
            ],
            "complex": [
                "real-time", "scalable", "microservices", "machine learning",
                "ai", "payment processing", "multi-tenant", "enterprise",
                "high availability", "load balancing", "caching"
            ]
        }
        
        scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            scores[level] = score
        
        # Determine complexity based on scores
        if scores["complex"] >= 2:
            return "complex"
        elif scores["moderate"] >= 2 or scores["complex"] >= 1:
            return "moderate"
        else:
            return "simple"
    
    def _extract_key_features(self, text: str) -> List[str]:
        """Extract key features from project description."""
        feature_patterns = {
            "User Authentication": ["login", "signup", "authentication", "user accounts"],
            "Database Integration": ["database", "data storage", "persistence", "records"],
            "Real-time Updates": ["real-time", "live updates", "websocket", "notifications"],
            "Search Functionality": ["search", "filter", "find", "query"],
            "File Upload": ["upload", "file", "image", "document"],
            "Payment Processing": ["payment", "checkout", "billing", "subscription"],
            "User Profiles": ["profile", "user info", "account settings"],
            "Admin Panel": ["admin", "management", "dashboard", "control panel"],
            "API Integration": ["api", "third-party", "integration", "external service"],
            "Mobile Responsive": ["mobile", "responsive", "tablet", "device"],
            "Email Notifications": ["email", "notifications", "alerts"],
            "Social Features": ["comments", "likes", "sharing", "social"],
            "Analytics": ["analytics", "tracking", "metrics", "reporting"],
            "Multi-language": ["multilingual", "i18n", "internationalization"],
            "Security": ["security", "encryption", "ssl", "secure"]
        }
        
        detected_features = []
        for feature, patterns in feature_patterns.items():
            if any(pattern in text for pattern in patterns):
                detected_features.append(feature)
        
        return detected_features
    
    def _recommend_tech_stack(self, project_type: str, features: List[str], complexity: str) -> Dict[str, str]:
        """Recommend optimal tech stack based on project analysis."""
        base_recommendations = self.tech_stack_recommendations.get(
            project_type, 
            self.tech_stack_recommendations["web_application"]
        )
        
        # Select specific technologies based on complexity and features
        recommendations = {}
        
        # Frontend selection
        if "Real-time Updates" in features:
            recommendations["frontend"] = "React + TypeScript"
        elif complexity == "complex":
            recommendations["frontend"] = "React + TypeScript"
        else:
            recommendations["frontend"] = base_recommendations["frontend"][0]
        
        # Backend selection
        if "API Integration" in features or complexity == "complex":
            recommendations["backend"] = "Node.js + Express"
        elif "Analytics" in features:
            recommendations["backend"] = "Python + FastAPI"
        else:
            recommendations["backend"] = base_recommendations["backend"][0]
        
        # Database selection
        if "Real-time Updates" in features:
            recommendations["database"] = "PostgreSQL + Redis"
        elif project_type == "data_dashboard":
            recommendations["database"] = "PostgreSQL"
        else:
            recommendations["database"] = base_recommendations["database"][0]
        
        # Additional tools based on features
        if "Payment Processing" in features:
            recommendations["payment"] = "Stripe API"
        
        if "File Upload" in features:
            recommendations["storage"] = "AWS S3 or Cloudinary"
        
        if "Real-time Updates" in features:
            recommendations["real_time"] = "Socket.io"
        
        if "Email Notifications" in features:
            recommendations["email"] = "SendGrid or Nodemailer"
        
        return recommendations
    
    def _identify_technical_challenges(self, text: str, project_type: str) -> List[str]:
        """Identify potential technical challenges."""
        challenges = []
        
        challenge_patterns = {
            "Scalability": ["scalable", "high traffic", "many users", "load"],
            "Real-time Synchronization": ["real-time", "live", "synchronization", "concurrent"],
            "Data Consistency": ["consistency", "transactions", "data integrity"],
            "Security": ["secure", "authentication", "authorization", "encryption"],
            "Performance": ["fast", "performance", "speed", "optimization"],
            "Integration Complexity": ["third-party", "api", "integration", "external"],
            "User Experience": ["ux", "user experience", "intuitive", "usable"],
            "Mobile Compatibility": ["mobile", "responsive", "cross-platform"],
            "Data Migration": ["migration", "existing data", "import"],
            "Compliance": ["gdpr", "compliance", "regulations", "privacy"]
        }
        
        for challenge, patterns in challenge_patterns.items():
            if any(pattern in text for pattern in patterns):
                challenges.append(challenge)
        
        return challenges
    
    def _determine_security_requirements(self, text: str, project_type: str) -> List[str]:
        """Determine security requirements based on project type and description."""
        security_requirements = ["Input validation", "HTTPS/SSL", "Error handling"]
        
        if any(term in text for term in ["login", "user", "account", "authentication"]):
            security_requirements.extend([
                "User authentication",
                "Password hashing",
                "Session management"
            ])
        
        if any(term in text for term in ["payment", "billing", "financial"]):
            security_requirements.extend([
                "PCI compliance",
                "Secure payment processing",
                "Data encryption"
            ])
        
        if any(term in text for term in ["admin", "management", "control"]):
            security_requirements.extend([
                "Role-based access control",
                "Admin authentication",
                "Audit logging"
            ])
        
        return security_requirements
    
    def _assess_performance_requirements(self, text: str, complexity: str) -> List[str]:
        """Assess performance requirements."""
        requirements = ["Fast page load times", "Optimized database queries"]
        
        if complexity == "complex" or any(term in text for term in ["scalable", "high traffic"]):
            requirements.extend([
                "Caching implementation",
                "Load balancing",
                "Database optimization",
                "CDN integration"
            ])
        
        if "real-time" in text:
            requirements.append("Low-latency real-time updates")
        
        return requirements
    
    def _assess_deployment_needs(self, text: str, complexity: str) -> List[str]:
        """Assess deployment and infrastructure needs."""
        needs = ["Environment configuration", "SSL certificate setup"]
        
        if complexity in ["moderate", "complex"]:
            needs.extend([
                "Database hosting",
                "File storage setup",
                "Monitoring and logging"
            ])
        
        if complexity == "complex":
            needs.extend([
                "Load balancer configuration",
                "Auto-scaling setup",
                "Backup and recovery"
            ])
        
        return needs
    
    def _estimate_timeline(self, complexity: str, feature_count: int) -> str:
        """Estimate development timeline."""
        base_times = {
            "simple": 2,
            "moderate": 5,
            "complex": 10
        }
        
        base_days = base_times.get(complexity, 5)
        feature_days = max(0, feature_count - 3) * 0.5  # Additional time for extra features
        
        total_days = base_days + feature_days
        
        if total_days <= 3:
            return "2-3 days"
        elif total_days <= 7:
            return "1 week"
        elif total_days <= 14:
            return "2 weeks"
        else:
            return "3+ weeks"
