"""
Child Agent - Main implementation

Integrates file management, application control, and system monitoring
into a cohesive agent that can execute laptop operations.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from agents.base_agent import BaseAgent, AgentAction, AgentResult, AgentStatus
from agents.child_agent.file_manager import FileManager
from agents.child_agent.app_controller import ApplicationController
from agents.child_agent.system_monitor import SystemMonitor
from utils import get_logger

logger = get_logger(__name__)


class ChildAgent(BaseAgent):
    """
    Child Agent - Executes basic laptop operations
    
    Capabilities:
    - File operations (read, write, delete, list)
    - Application control (launch, close, list processes)
    - System monitoring (CPU, memory, disk, network)
    - Keyboard and mouse automation
    
    The Child Agent is supervised by the Parent Agent and executes
    actions based on LLM-generated plans.
    """
    
    # Define available action types
    ACTION_TYPES = {
        # File operations
        'read_file', 'write_file', 'delete_file', 'list_directory', 'get_file_info',
        # Application operations
        'launch_app', 'close_app', 'list_processes', 'get_process_info',
        'type_text', 'press_key', 'click_mouse', 'get_screen_size',
        # System monitoring
        'get_cpu_info', 'get_memory_info', 'get_disk_info', 'get_all_disks_info',
        'get_network_info', 'get_network_interfaces', 'get_system_info',
        'get_current_metrics', 'get_top_processes', 'check_resource_thresholds'
    }
    
    def __init__(
        self,
        name: str = "ChildAgent",
        config: Dict[str, Any] = None,
        allowed_paths: list = None,
        enable_safety_checks: bool = True
    ):
        """
        Initialize Child Agent
        
        Args:
            name: Agent name
            config: Configuration dictionary
            allowed_paths: Allowed file paths (whitelist)
            enable_safety_checks: Enable safety checks for operations
        """
        super().__init__(name, config)
        
        self.enable_safety_checks = enable_safety_checks
        
        # Initialize modules
        self.file_manager = FileManager(
            allowed_paths=allowed_paths,
            max_file_size_mb=config.get('max_file_size_mb', 100) if config else 100
        )
        
        self.app_controller = ApplicationController(
            timeout=config.get('timeout', 30) if config else 30
        )
        
        self.system_monitor = SystemMonitor(
            history_size=config.get('history_size', 100) if config else 100
        )
        
        logger.info(f"ChildAgent '{name}' initialized (safety_checks={enable_safety_checks})")
    
    async def initialize(self) -> bool:
        """
        Initialize the agent
        
        Returns:
            True if successful
        """
        logger.info(f"Initializing {self.name}")
        
        try:
            # Perform any initialization tasks
            self.status = AgentStatus.IDLE
            
            # Get initial system metrics
            self.system_monitor.get_current_metrics()
            
            logger.success(f"{self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing {self.name}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def shutdown(self) -> bool:
        """
        Shutdown the agent
        
        Returns:
            True if successful
        """
        logger.info(f"Shutting down {self.name}")
        
        try:
            self.status = AgentStatus.STOPPED
            logger.success(f"{self.name} shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down {self.name}: {e}")
            return False
    
    async def execute_action(self, action: AgentAction) -> AgentResult:
        """
        Execute a specific action
        
        Args:
            action: Action to execute
            
        Returns:
            Result of the action
        """
        logger.info(f"Executing action: {action.action_type} (ID: {action.action_id})")
        
        start_time = datetime.now()
        
        # Validate action type
        if action.action_type not in self.ACTION_TYPES:
            error = f"Unknown action type: {action.action_type}"
            logger.error(error)
            return AgentResult(
                action_id=action.action_id,
                success=False,
                error=error
            )
        
        # Update status
        self.status = AgentStatus.RUNNING
        
        try:
            # Route to appropriate handler
            result = await self._route_action(action)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Record action
            self._record_action(result)
            
            # Update status
            self.status = AgentStatus.IDLE
            
            logger.success(f"Action completed: {action.action_type} ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            error = f"Error executing action: {e}"
            logger.error(error)
            
            self.status = AgentStatus.ERROR
            
            result = AgentResult(
                action_id=action.action_id,
                success=False,
                error=error,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            
            self._record_action(result)
            return result
    
    async def _route_action(self, action: AgentAction) -> AgentResult:
        """
        Route action to appropriate handler
        
        Args:
            action: Action to route
            
        Returns:
            Action result
        """
        action_type = action.action_type
        params = action.parameters
        
        # File operations
        if action_type == 'read_file':
            operation = self.file_manager.read_file(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'write_file':
            operation = self.file_manager.write_file(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'delete_file':
            operation = self.file_manager.delete_file(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'list_directory':
            operation = self.file_manager.list_directory(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'get_file_info':
            operation = self.file_manager.get_file_info(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        # Application operations
        elif action_type == 'launch_app':
            operation = self.app_controller.launch_app(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'close_app':
            operation = self.app_controller.close_app(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'list_processes':
            operation = self.app_controller.list_processes(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'get_process_info':
            operation = self.app_controller.get_process_info(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'type_text':
            operation = self.app_controller.type_text(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'press_key':
            operation = self.app_controller.press_key(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'click_mouse':
            operation = self.app_controller.click_mouse(**params)
            return self._convert_operation_to_result(action.action_id, operation)
        
        elif action_type == 'get_screen_size':
            operation = self.app_controller.get_screen_size()
            return self._convert_operation_to_result(action.action_id, operation)
        
        # System monitoring
        elif action_type == 'get_cpu_info':
            info = self.system_monitor.get_cpu_info()
            return AgentResult(
                action_id=action.action_id,
                success='error' not in info,
                result=info,
                error=info.get('error')
            )
        
        elif action_type == 'get_memory_info':
            info = self.system_monitor.get_memory_info()
            return AgentResult(
                action_id=action.action_id,
                success='error' not in info,
                result=info,
                error=info.get('error')
            )
        
        elif action_type == 'get_disk_info':
            info = self.system_monitor.get_disk_info(**params)
            return AgentResult(
                action_id=action.action_id,
                success='error' not in info,
                result=info,
                error=info.get('error')
            )
        
        elif action_type == 'get_all_disks_info':
            disks = self.system_monitor.get_all_disks_info()
            return AgentResult(
                action_id=action.action_id,
                success=True,
                result=disks
            )
        
        elif action_type == 'get_network_info':
            info = self.system_monitor.get_network_info()
            return AgentResult(
                action_id=action.action_id,
                success='error' not in info,
                result=info,
                error=info.get('error')
            )
        
        elif action_type == 'get_network_interfaces':
            interfaces = self.system_monitor.get_network_interfaces()
            return AgentResult(
                action_id=action.action_id,
                success='error' not in interfaces,
                result=interfaces,
                error=interfaces.get('error')
            )
        
        elif action_type == 'get_system_info':
            info = self.system_monitor.get_system_info()
            return AgentResult(
                action_id=action.action_id,
                success='error' not in info,
                result=info,
                error=info.get('error')
            )
        
        elif action_type == 'get_current_metrics':
            metrics = self.system_monitor.get_current_metrics()
            return AgentResult(
                action_id=action.action_id,
                success=True,
                result=metrics.dict()
            )
        
        elif action_type == 'get_top_processes':
            processes = self.system_monitor.get_top_processes(**params)
            return AgentResult(
                action_id=action.action_id,
                success=True,
                result=processes
            )
        
        elif action_type == 'check_resource_thresholds':
            result = self.system_monitor.check_resource_thresholds(**params)
            return AgentResult(
                action_id=action.action_id,
                success='error' not in result,
                result=result,
                error=result.get('error')
            )
        
        else:
            return AgentResult(
                action_id=action.action_id,
                success=False,
                error=f"Unhandled action type: {action_type}"
            )
    
    def _convert_operation_to_result(self, action_id: str, operation) -> AgentResult:
        """
        Convert FileOperation or AppOperation to AgentResult
        
        Args:
            action_id: Action ID
            operation: Operation result object
            
        Returns:
            AgentResult
        """
        return AgentResult(
            action_id=action_id,
            success=operation.success,
            result=operation.metadata if operation.success else None,
            error=operation.error
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            'name': self.name,
            'type': 'child_agent',
            'status': self.status.value,
            'capabilities': {
                'file_operations': [
                    'read_file', 'write_file', 'delete_file',
                    'list_directory', 'get_file_info'
                ],
                'application_operations': [
                    'launch_app', 'close_app', 'list_processes',
                    'get_process_info', 'type_text', 'press_key',
                    'click_mouse', 'get_screen_size'
                ],
                'system_monitoring': [
                    'get_cpu_info', 'get_memory_info', 'get_disk_info',
                    'get_all_disks_info', 'get_network_info', 'get_network_interfaces',
                    'get_system_info', 'get_current_metrics', 'get_top_processes',
                    'check_resource_thresholds'
                ]
            },
            'safety_checks_enabled': self.enable_safety_checks,
            'total_actions_executed': len(self.action_history)
        }
