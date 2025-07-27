"""
LLM Agent management for Jarvis Voice Assistant.

This module handles the language model agent initialization, configuration,
and interaction with proper error handling and tool integration.
"""

import logging
from typing import Optional, Dict, Any, List
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from ..config import LLMConfig
from ..exceptions import LLMError, ModelLoadError, ModelInferenceError, ToolError


logger = logging.getLogger(__name__)


class JarvisAgent:
    """
    Manages the LLM agent for the Jarvis voice assistant.
    
    This class handles language model initialization, tool integration,
    and conversation processing with proper error handling.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the Jarvis agent.
        
        Args:
            config: LLM configuration settings
        """
        self.config = config
        self.llm: Optional[ChatOllama] = None
        self.agent_executor: Optional[AgentExecutor] = None
        self.tools: List[BaseTool] = []
        self._is_initialized = False
        
        # Default system prompt
        self.system_prompt = """You are Jarvis, a helpful AI assistant. You have access to tools and should use them appropriately.

When to use tools:
- Memory requests (remember, recall, store information) → use Memory Storage tools
- Current time queries → use get_current_time tool
- UI control requests → use appropriate UI tools
- Real-time data requests → use relevant tools

When to answer directly (NO TOOLS):
- General knowledge questions (facts, concepts, explanations)
- Questions about how things work
- Historical information
- Scientific explanations
- Definitions and descriptions

MEMORY FUNCTIONALITY:
- For "Remember that..." → use add_observations tool
- For "What do you remember..." → use search_nodes tool
- For "Do you remember..." → use read_graph tool
- For "Tell me what you know..." → use search_nodes tool
- For "What have I told you..." → use search_nodes tool
- For questions about preferences, hobbies, etc. → use search_nodes tool

Be friendly and professional like Tony Stark's Jarvis. Keep responses brief and conversational.

EXAMPLES:
❌ WRONG: "I don't have a tool for cars"
✅ CORRECT: "Cars are motor vehicles with four wheels, powered by internal combustion engines or electric motors..."

✅ CORRECT: For "What time is it?" → Use get_current_time tool
✅ CORRECT: For "Remember that I like coffee" → Use add_observations tool
✅ CORRECT: For "What do you remember about my preferences" → Use search_nodes tool
✅ CORRECT: For "Do you remember anything about me" → Use search_nodes tool"""

        logger.info(f"JarvisAgent initialized with config: {config}")
    
    def initialize(self, tools: Optional[List[BaseTool]] = None) -> None:
        """
        Initialize the LLM and agent with the configured settings.
        
        Args:
            tools: List of tools to make available to the agent
            
        Raises:
            ModelLoadError: If model loading fails
            LLMError: If agent initialization fails
        """
        try:
            logger.info(f"Initializing LLM model: {self.config.model}")
            
            # Initialize the language model
            self.llm = ChatOllama(
                model=self.config.model,
                reasoning=self.config.reasoning,
                temperature=self.config.temperature,
                verbose=self.config.verbose
            )
            
            # Test the model with a simple query
            test_response = self.llm.invoke("Hello")
            logger.debug(f"Model test response: {test_response}")
            
            # Set up tools
            if tools:
                self.tools = tools
                logger.info(f"Loaded {len(self.tools)} tools: {[tool.name for tool in self.tools]}")
            
            # Create the agent if tools are available
            if self.tools:
                self._create_agent()
            
            self._is_initialized = True
            logger.info("JarvisAgent initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize LLM model '{self.config.model}': {str(e)}"
            logger.error(error_msg)
            raise ModelLoadError(error_msg, model_name=self.config.model) from e
    
    def _create_agent(self) -> None:
        """Create the tool-calling agent."""
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Create the agent
            agent = create_tool_calling_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.config.verbose,
                handle_parsing_errors=True,
                max_iterations=5,
                max_execution_time=30
            )
            
            logger.info("Agent executor created successfully")
            
        except Exception as e:
            error_msg = f"Failed to create agent: {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
    
    def is_initialized(self) -> bool:
        """
        Check if the agent is properly initialized.
        
        Returns:
            True if agent is initialized, False otherwise
        """
        return self._is_initialized and self.llm is not None
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: User's input text
            
        Returns:
            Agent's response text
            
        Raises:
            ModelInferenceError: If model inference fails
            ToolError: If tool execution fails
        """
        if not self.is_initialized():
            raise LLMError("Agent not initialized. Call initialize() first.")
        
        if not user_input or not user_input.strip():
            return "I didn't hear anything. Could you please repeat that?"
        
        try:
            logger.debug(f"Processing input: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
            
            if self.agent_executor:
                # Use agent executor for tool-enabled responses
                response = self.agent_executor.invoke({"input": user_input})
                output = response.get("output", "I'm sorry, I couldn't process that request.")


            else:
                # Direct LLM response without tools
                response = self.llm.invoke(user_input)
                output = response.content if hasattr(response, 'content') else str(response)
            
            logger.debug(f"Generated response: '{output[:100]}{'...' if len(output) > 100 else ''}'")
            return output
            
        except Exception as e:
            error_msg = f"Failed to process input: {str(e)}"
            logger.error(error_msg)
            raise ModelInferenceError(
                error_msg,
                input_text=user_input,
                model_name=self.config.model
            ) from e


    def add_tools(self, tools: List[BaseTool]) -> None:
        """
        Add tools to the agent.
        
        Args:
            tools: List of tools to add
            
        Raises:
            LLMError: If tool addition fails
        """
        try:
            self.tools.extend(tools)
            logger.info(f"Added {len(tools)} tools: {[tool.name for tool in tools]}")
            
            # Recreate agent if already initialized
            if self.is_initialized() and self.llm:
                self._create_agent()
                
        except Exception as e:
            error_msg = f"Failed to add tools: {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the agent.
        
        Args:
            tool_name: Name of the tool to remove
            
        Returns:
            True if tool was removed, False if not found
            
        Raises:
            LLMError: If tool removal fails
        """
        try:
            original_count = len(self.tools)
            self.tools = [tool for tool in self.tools if tool.name != tool_name]
            
            if len(self.tools) < original_count:
                logger.info(f"Removed tool: {tool_name}")
                
                # Recreate agent if already initialized
                if self.is_initialized() and self.llm:
                    self._create_agent()
                
                return True
            else:
                logger.warning(f"Tool not found: {tool_name}")
                return False
                
        except Exception as e:
            error_msg = f"Failed to remove tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set a custom system prompt.
        
        Args:
            prompt: New system prompt
            
        Raises:
            LLMError: If prompt setting fails
        """
        try:
            self.system_prompt = prompt
            logger.info("System prompt updated")
            
            # Recreate agent if already initialized
            if self.is_initialized() and self.llm and self.tools:
                self._create_agent()
                
        except Exception as e:
            error_msg = f"Failed to set system prompt: {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.config.model,
            "temperature": self.config.temperature,
            "reasoning": self.config.reasoning,
            "verbose": self.config.verbose,
            "max_tokens": self.config.max_tokens,
            "is_initialized": self.is_initialized(),
            "tools_count": len(self.tools),
            "available_tools": self.get_available_tools()
        }
    
    def test_model(self, test_input: str = "Hello, can you hear me?") -> bool:
        """
        Test the model with a simple input.
        
        Args:
            test_input: Test input to send to the model
            
        Returns:
            True if test successful, False otherwise
        """
        if not self.is_initialized():
            logger.error("Cannot test model: not initialized")
            return False
        
        try:
            logger.info("Testing model...")
            response = self.process_input(test_input)
            logger.info(f"Model test successful. Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            return True
        except Exception as e:
            logger.error(f"Model test failed: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Clean up agent resources."""
        logger.info("Cleaning up agent resources")
        self.llm = None
        self.agent_executor = None
        self.tools.clear()
        self._is_initialized = False
