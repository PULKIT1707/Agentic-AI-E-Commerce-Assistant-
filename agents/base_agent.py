"""
Base Agent Class for E-Commerce Assistant Agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the e-commerce assistant system."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            config: Configuration dictionary for the agent
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Args:
            query: Input query containing parameters for the agent
            
        Returns:
            Dictionary containing the agent's results
        """
        pass
    
    def validate_input(self, query: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that required fields are present in the query.
        
        Args:
            query: Input query dictionary
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in query]
        if missing_fields:
            self.logger.warning(f"Missing required fields: {missing_fields}")
            return False
        return True
    
    def log_result(self, result: Dict[str, Any]) -> None:
        """Log the agent's result for debugging."""
        self.logger.info(f"{self.name} completed execution")
        self.logger.debug(f"Result: {result}")
