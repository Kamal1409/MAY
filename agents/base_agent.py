"""Base agent class for all MAY agents"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class AgentAction(BaseModel):
    """Represents an action to be executed by an agent"""
    action_id: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=0, ge=0, le=10)


class AgentResult(BaseModel):
    """Represents the result of an agent action"""
    action_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0  # seconds


class BaseAgent(ABC):
    """
    Base class for all agents in the MAY system
    
    Provides common functionality for agent lifecycle, action execution,
    and communication with other agents.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize base agent
        
        Args:
            name: Agent name/identifier
            config: Agent-specific configuration
        """
        self.name = name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.action_history: List[AgentResult] = []
        
    @abstractmethod
    async def execute_action(self, action: AgentAction) -> AgentResult:
        """
        Execute a specific action
        
        Args:
            action: Action to execute
            
        Returns:
            Result of the action execution
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent and its resources
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown the agent and cleanup resources
        
        Returns:
            True if shutdown successful, False otherwise
        """
        pass
    
    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
    
    def get_action_history(self, limit: int = 10) -> List[AgentResult]:
        """
        Get recent action history
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent action results
        """
        return self.action_history[-limit:]
    
    def _record_action(self, result: AgentResult):
        """Record an action result in history"""
        self.action_history.append(result)
        
        # Keep history size manageable
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-500:]
