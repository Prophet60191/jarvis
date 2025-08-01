"""
Professional Application Builder Plugin

Builds complete, professional applications following software engineering
best practices and the 7-phase development workflow.
"""

import logging
import asyncio
from typing import List
from langchain.tools import tool
from langchain_core.tools import BaseTool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from jarvis.plugins.base import PluginBase, PluginMetadata
from jarvis.core.project_analyzer import ProjectRequirementsAnalyzer

logger = logging.getLogger(__name__)


@tool
def build_professional_application(
    project_description: str,
    requirements: str = "",
    tech_stack: str = "auto",
    project_name: str = "",
    watch_workflow: str = "ask"
) -> str:
    """
    Build a complete, professional application following software engineering best practices.
    
    Use when user requests:
    - "Build me an app for [purpose]"
    - "Create a [type] application"
    - "Develop a professional [project] system"
    - "Make me a production-ready [application]"
    - "I need a [description] application"
    - "Can you build a [type] app"
    - "Create a full-stack [application]"
    
    This tool follows a comprehensive 9-phase development workflow:
    1. Research & Analysis - Technology selection and architecture planning
    2. Project Initialization - Setup and configuration
    2.5. Environment Setup & Dependencies - Virtual environment and package management
    3. Frontend Development - User interface and experience
    4. Backend Development - Server logic and APIs
    5. Database Integration - Data persistence and management
    6. Testing & Quality Assurance - Comprehensive validation
    6.5. Runtime Verification & System Testing - Ensure application actually works
    7. Deployment & Operations - Production readiness
    
    Args:
        project_description: What the application should do and its main purpose
        requirements: Specific features, constraints, or technical requirements
        tech_stack: Preferred technologies (auto-selects optimal stack if not specified)
        project_name: Name for the project directory (auto-generated if not provided)
        watch_workflow: Whether to show real-time workflow ("ask", "yes", "no")
        
    Returns:
        Complete application development results with project location and details
    """
    try:
        logger.info(f"Starting professional application build: {project_description}")

        # Handle workflow watching preference
        should_watch = False
        if watch_workflow.lower() == "ask":
            # In a real implementation, this would prompt the user
            # For now, default to no watching to avoid complexity
            should_watch = False
        elif watch_workflow.lower() == "yes":
            should_watch = True
        else:
            should_watch = False

        # Generate project name if not provided
        if not project_name:
            project_name = _generate_project_name(project_description)

        # Create Smart App Builder Coordinator
        from ...core.smart_app_builder import SmartAppBuilderCoordinator

        coordinator = SmartAppBuilderCoordinator(
            project_name=project_name,
            project_description=project_description,
            requirements=requirements,
            tech_stack=tech_stack,
            watch_workflow=should_watch
        )

        # Execute complete workflow
        result = coordinator.execute_complete_workflow()
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to build professional application: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}\n\nPlease check the error details and try again."


@tool
def analyze_project_requirements(project_description: str, additional_requirements: str = "") -> str:
    """
    Analyze project requirements and provide detailed recommendations.
    
    Use when user wants to:
    - "Analyze my project requirements"
    - "What tech stack should I use for [project]?"
    - "Help me plan a [type] application"
    - "What's the best approach for building [project]?"
    
    Args:
        project_description: Description of the project to analyze
        additional_requirements: Any additional specific requirements or constraints
        
    Returns:
        Detailed analysis with tech stack recommendations, complexity assessment, and implementation guidance
    """
    try:
        analyzer = ProjectRequirementsAnalyzer()
        analysis = analyzer.analyze_project(project_description, additional_requirements)
        
        report = f"""
📊 PROJECT REQUIREMENTS ANALYSIS

🎯 PROJECT OVERVIEW:
• Type: {analysis.project_type.replace('_', ' ').title()}
• Complexity: {analysis.complexity_level.title()}
• Estimated Timeline: {analysis.estimated_timeline}

🛠️ RECOMMENDED TECH STACK:
"""
        
        for component, technology in analysis.recommended_tech_stack.items():
            report += f"• {component.title()}: {technology}\n"
        
        report += f"""
✨ KEY FEATURES IDENTIFIED:
{chr(10).join(f'• {feature}' for feature in analysis.key_features)}

⚠️ TECHNICAL CHALLENGES:
{chr(10).join(f'• {challenge}' for challenge in analysis.technical_challenges)}

🔒 SECURITY REQUIREMENTS:
{chr(10).join(f'• {req}' for req in analysis.security_requirements)}

⚡ PERFORMANCE CONSIDERATIONS:
{chr(10).join(f'• {req}' for req in analysis.performance_requirements)}

🚀 DEPLOYMENT NEEDS:
{chr(10).join(f'• {need}' for need in analysis.deployment_considerations)}

💡 RECOMMENDATIONS:
• Follow the 7-phase professional development workflow
• Implement security measures from the beginning
• Plan for scalability based on expected usage
• Include comprehensive testing throughout development
• Prepare for production deployment early in the process

Ready to build? Use the 'build_professional_application' tool to start development!
"""
        
        return report
        
    except Exception as e:
        error_msg = f"Failed to analyze project requirements: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


@tool
def get_workflow_guidance(phase: str = "overview") -> str:
    """
    Get detailed guidance about the professional development workflow.
    
    Use when user asks:
    - "What is the development workflow?"
    - "How does the app building process work?"
    - "What are the development phases?"
    - "Tell me about phase [number]"
    
    Args:
        phase: Specific phase to get guidance for ("overview", "1", "2", etc.) or "all"
        
    Returns:
        Detailed workflow guidance and best practices
    """
    try:
        from jarvis.core.workflow_standards import ProfessionalWorkflowStandards
        
        standards = ProfessionalWorkflowStandards()
        
        if phase.lower() == "overview":
            return f"""
🏗️ PROFESSIONAL DEVELOPMENT WORKFLOW

This enhanced 9-phase workflow ensures every application built follows software engineering best practices:

📋 PHASE OVERVIEW:
1. **Research & Analysis** - Technology selection and architecture planning
2. **Project Initialization** - Setup, configuration, and foundation
2.5. **Environment Setup & Dependencies** - Virtual environment and package management
3. **Frontend Development** - User interface and experience implementation
4. **Backend Development** - Server logic, APIs, and business rules
5. **Database Integration** - Data persistence and management systems
6. **Testing & Quality Assurance** - Comprehensive validation and testing
6.5. **Runtime Verification & System Testing** - Ensure application actually works
7. **Deployment & Operations** - Production readiness and monitoring

🎯 WORKFLOW BENEFITS:
• Ensures professional-quality applications
• Follows software engineering best practices
• Creates proper development environments
• Manages dependencies and system compatibility
• Includes security and performance from the start
• Provides comprehensive testing and validation
• Verifies applications actually run correctly
• Results in production-ready, maintainable code
• Includes complete documentation and procedures

📚 For detailed guidance on any phase, ask: "Tell me about phase [number]"
"""
        
        elif phase.lower() == "all":
            return standards.get_complete_workflow()
        
        elif (phase.replace('.', '').replace('5', '').isdigit() and
              (1 <= float(phase) <= 7 or phase in ['2.5', '6.5'])):
            phase_num = float(phase)
            phase_req = standards.get_phase_requirements(phase_num)
            
            return f"""
📋 PHASE {phase_num}: {phase_req.name.upper()}

🎯 DESCRIPTION:
{phase_req.description}

📦 DELIVERABLES:
{chr(10).join(f'• {deliverable}' for deliverable in phase_req.deliverables)}

✅ QUALITY CHECKS:
{chr(10).join(f'• {check}' for check in phase_req.quality_checks)}

🔗 DEPENDENCIES:
{chr(10).join(f'• {dep}' for dep in phase_req.dependencies) if phase_req.dependencies else '• None (can start immediately)'}

💡 This phase is automatically executed as part of the professional application building process.
"""
        
        else:
            return f"""
❌ Invalid phase: {phase}

Valid options:
• "overview" - Get workflow overview
• "all" - Get complete workflow details
• "1" through "7" - Get specific phase details
• "2.5" - Environment Setup & Dependencies phase
• "6.5" - Runtime Verification & System Testing phase

Example: get_workflow_guidance("2.5") for Environment Setup phase details
"""
        
    except Exception as e:
        error_msg = f"Failed to get workflow guidance: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


def _generate_project_name(description: str) -> str:
    """Generate a project name from description."""
    import re
    
    # Extract key words from description
    words = re.findall(r'\b\w+\b', description.lower())
    
    # Filter out common words
    stop_words = {'a', 'an', 'the', 'for', 'with', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from', 'by', 'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'build', 'create', 'make', 'develop', 'app', 'application', 'system', 'me', 'i', 'my'}
    
    meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Take first 2-3 meaningful words
    if len(meaningful_words) >= 2:
        project_name = '_'.join(meaningful_words[:3])
    elif len(meaningful_words) == 1:
        project_name = f"{meaningful_words[0]}_app"
    else:
        project_name = "jarvis_app"
    
    return project_name


class ProfessionalAppBuilderPlugin(PluginBase):
    """Plugin for professional application development workflow."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="ProfessionalAppBuilder",
            version="1.0.0",
            description="Build professional applications following software engineering best practices and 7-phase development workflow",
            author="Jarvis Team",
            dependencies=["aider"]
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return the professional app builder tools."""
        return [
            build_professional_application,
            analyze_project_requirements,
            get_workflow_guidance
        ]


# Required variables for plugin discovery system
PLUGIN_CLASS = ProfessionalAppBuilderPlugin
PLUGIN_METADATA = ProfessionalAppBuilderPlugin().get_metadata()
