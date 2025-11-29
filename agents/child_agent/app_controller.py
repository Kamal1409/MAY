"""
Application Controller Module for Child Agent

Provides application and process control with window management
and automation capabilities.
"""

import os
import subprocess
import psutil
import pyautogui
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

# Configure pyautogui safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


class AppOperation(BaseModel):
    """Represents an application operation result"""
    operation: str
    app_name: Optional[str] = None
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessInfo(BaseModel):
    """Information about a running process"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_mb: float
    create_time: str


class ApplicationController:
    """
    Manages application launching, control, and automation
    
    Features:
    - Launch and close applications
    - Process management
    - Window control (focus, resize, minimize)
    - Keyboard and mouse automation
    - Safety checks and timeouts
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize Application Controller
        
        Args:
            timeout: Default timeout for operations in seconds
        """
        self.timeout = timeout
        self.launched_processes: Dict[str, int] = {}  # app_name -> pid
        
        logger.info(f"ApplicationController initialized with timeout={timeout}s")
    
    def launch_app(
        self,
        app_path: str,
        args: List[str] = None,
        wait: bool = False
    ) -> AppOperation:
        """
        Launch an application
        
        Args:
            app_path: Path to application executable or command name
            args: Command line arguments
            wait: Wait for application to complete
            
        Returns:
            AppOperation result
        """
        logger.info(f"Launching application: {app_path}")
        
        try:
            # Build command
            cmd = [app_path]
            if args:
                cmd.extend(args)
            
            # Launch process
            if wait:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                logger.success(f"Application completed: {app_path}")
                return AppOperation(
                    operation="launch",
                    app_name=os.path.basename(app_path),
                    success=result.returncode == 0,
                    error=result.stderr if result.returncode != 0 else None,
                    metadata={
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Store PID
                app_name = os.path.basename(app_path)
                self.launched_processes[app_name] = process.pid
                
                logger.success(f"Application launched: {app_path} (PID: {process.pid})")
                return AppOperation(
                    operation="launch",
                    app_name=app_name,
                    success=True,
                    metadata={
                        'pid': process.pid,
                        'command': ' '.join(cmd)
                    }
                )
                
        except subprocess.TimeoutExpired:
            error = f"Application launch timed out after {self.timeout}s"
            logger.error(error)
            return AppOperation(
                operation="launch",
                app_name=os.path.basename(app_path),
                success=False,
                error=error
            )
        except FileNotFoundError:
            error = f"Application not found: {app_path}"
            logger.error(error)
            return AppOperation(
                operation="launch",
                app_name=os.path.basename(app_path),
                success=False,
                error=error
            )
        except Exception as e:
            error = f"Error launching application: {e}"
            logger.error(error)
            return AppOperation(
                operation="launch",
                app_name=os.path.basename(app_path),
                success=False,
                error=error
            )
    
    def close_app(self, pid: int = None, app_name: str = None, force: bool = False) -> AppOperation:
        """
        Close an application
        
        Args:
            pid: Process ID to close
            app_name: Application name to close (uses stored PID)
            force: Force kill the process
            
        Returns:
            AppOperation result
        """
        logger.info(f"Closing application: pid={pid}, app_name={app_name}, force={force}")
        
        # Determine PID
        if pid is None and app_name:
            pid = self.launched_processes.get(app_name)
            if pid is None:
                error = f"No PID found for application: {app_name}"
                logger.error(error)
                return AppOperation(
                    operation="close",
                    app_name=app_name,
                    success=False,
                    error=error
                )
        
        if pid is None:
            error = "Either pid or app_name must be provided"
            logger.error(error)
            return AppOperation(
                operation="close",
                success=False,
                error=error
            )
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if force:
                process.kill()
                logger.success(f"Force killed process: {process_name} (PID: {pid})")
            else:
                process.terminate()
                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                    logger.success(f"Terminated process: {process_name} (PID: {pid})")
                except psutil.TimeoutExpired:
                    # Force kill if terminate didn't work
                    process.kill()
                    logger.warning(f"Force killed process after terminate timeout: {process_name}")
            
            # Remove from tracked processes
            if app_name and app_name in self.launched_processes:
                del self.launched_processes[app_name]
            
            return AppOperation(
                operation="close",
                app_name=process_name,
                success=True,
                metadata={'pid': pid, 'forced': force}
            )
            
        except psutil.NoSuchProcess:
            error = f"Process not found: PID {pid}"
            logger.error(error)
            return AppOperation(
                operation="close",
                success=False,
                error=error,
                metadata={'pid': pid}
            )
        except psutil.AccessDenied:
            error = f"Access denied to close process: PID {pid}"
            logger.error(error)
            return AppOperation(
                operation="close",
                success=False,
                error=error,
                metadata={'pid': pid}
            )
        except Exception as e:
            error = f"Error closing application: {e}"
            logger.error(error)
            return AppOperation(
                operation="close",
                success=False,
                error=error,
                metadata={'pid': pid}
            )
    
    def list_processes(self, filter_name: str = None) -> AppOperation:
        """
        List running processes
        
        Args:
            filter_name: Optional filter by process name
            
        Returns:
            AppOperation with process list in metadata
        """
        logger.info(f"Listing processes (filter={filter_name})")
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    info = proc.info
                    
                    # Apply filter if specified
                    if filter_name and filter_name.lower() not in info['name'].lower():
                        continue
                    
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'status': info['status'],
                        'cpu_percent': info['cpu_percent'],
                        'memory_mb': info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0,
                        'create_time': datetime.fromtimestamp(info['create_time']).isoformat() if info['create_time'] else None
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.success(f"Listed {len(processes)} processes")
            return AppOperation(
                operation="list_processes",
                success=True,
                metadata={
                    'processes': processes,
                    'count': len(processes),
                    'filter': filter_name
                }
            )
            
        except Exception as e:
            error = f"Error listing processes: {e}"
            logger.error(error)
            return AppOperation(
                operation="list_processes",
                success=False,
                error=error
            )
    
    def get_process_info(self, pid: int) -> AppOperation:
        """
        Get detailed information about a process
        
        Args:
            pid: Process ID
            
        Returns:
            AppOperation with process info in metadata
        """
        logger.info(f"Getting process info for PID: {pid}")
        
        try:
            process = psutil.Process(pid)
            
            info = {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'num_threads': process.num_threads(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'exe': process.exe(),
                'cwd': process.cwd(),
                'cmdline': ' '.join(process.cmdline())
            }
            
            logger.success(f"Got process info for: {info['name']} (PID: {pid})")
            return AppOperation(
                operation="get_process_info",
                app_name=info['name'],
                success=True,
                metadata=info
            )
            
        except psutil.NoSuchProcess:
            error = f"Process not found: PID {pid}"
            logger.error(error)
            return AppOperation(
                operation="get_process_info",
                success=False,
                error=error
            )
        except psutil.AccessDenied:
            error = f"Access denied for process: PID {pid}"
            logger.error(error)
            return AppOperation(
                operation="get_process_info",
                success=False,
                error=error
            )
        except Exception as e:
            error = f"Error getting process info: {e}"
            logger.error(error)
            return AppOperation(
                operation="get_process_info",
                success=False,
                error=error
            )
    
    def type_text(self, text: str, interval: float = 0.05) -> AppOperation:
        """
        Type text using keyboard automation
        
        Args:
            text: Text to type
            interval: Interval between keystrokes in seconds
            
        Returns:
            AppOperation result
        """
        logger.info(f"Typing text: {text[:50]}...")
        
        try:
            pyautogui.write(text, interval=interval)
            
            logger.success(f"Typed {len(text)} characters")
            return AppOperation(
                operation="type_text",
                success=True,
                metadata={
                    'length': len(text),
                    'interval': interval
                }
            )
            
        except Exception as e:
            error = f"Error typing text: {e}"
            logger.error(error)
            return AppOperation(
                operation="type_text",
                success=False,
                error=error
            )
    
    def press_key(self, key: str, presses: int = 1) -> AppOperation:
        """
        Press a keyboard key
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'esc')
            presses: Number of times to press
            
        Returns:
            AppOperation result
        """
        logger.info(f"Pressing key: {key} ({presses} times)")
        
        try:
            pyautogui.press(key, presses=presses)
            
            logger.success(f"Pressed key: {key}")
            return AppOperation(
                operation="press_key",
                success=True,
                metadata={'key': key, 'presses': presses}
            )
            
        except Exception as e:
            error = f"Error pressing key: {e}"
            logger.error(error)
            return AppOperation(
                operation="press_key",
                success=False,
                error=error
            )
    
    def click_mouse(self, x: int = None, y: int = None, clicks: int = 1, button: str = 'left') -> AppOperation:
        """
        Click mouse at position
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            clicks: Number of clicks
            button: Mouse button ('left', 'right', 'middle')
            
        Returns:
            AppOperation result
        """
        logger.info(f"Clicking mouse at ({x}, {y}), button={button}, clicks={clicks}")
        
        try:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            else:
                pyautogui.click(clicks=clicks, button=button)
            
            logger.success(f"Clicked mouse: {clicks} time(s)")
            return AppOperation(
                operation="click_mouse",
                success=True,
                metadata={'x': x, 'y': y, 'clicks': clicks, 'button': button}
            )
            
        except Exception as e:
            error = f"Error clicking mouse: {e}"
            logger.error(error)
            return AppOperation(
                operation="click_mouse",
                success=False,
                error=error
            )
    
    def get_screen_size(self) -> AppOperation:
        """
        Get screen dimensions
        
        Returns:
            AppOperation with screen size in metadata
        """
        logger.info("Getting screen size")
        
        try:
            size = pyautogui.size()
            
            logger.success(f"Screen size: {size.width}x{size.height}")
            return AppOperation(
                operation="get_screen_size",
                success=True,
                metadata={
                    'width': size.width,
                    'height': size.height
                }
            )
            
        except Exception as e:
            error = f"Error getting screen size: {e}"
            logger.error(error)
            return AppOperation(
                operation="get_screen_size",
                success=False,
                error=error
            )
    
    def get_mouse_position(self) -> AppOperation:
        """
        Get current mouse position
        
        Returns:
            AppOperation with mouse position in metadata
        """
        try:
            pos = pyautogui.position()
            
            return AppOperation(
                operation="get_mouse_position",
                success=True,
                metadata={'x': pos.x, 'y': pos.y}
            )
            
        except Exception as e:
            error = f"Error getting mouse position: {e}"
            logger.error(error)
            return AppOperation(
                operation="get_mouse_position",
                success=False,
                error=error
            )
