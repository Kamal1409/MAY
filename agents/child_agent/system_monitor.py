"""
System Monitor Module for Child Agent

Provides system information gathering including CPU, memory, disk,
network, and process monitoring.
"""

import psutil
import platform
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger


class SystemMetrics(BaseModel):
    """System metrics snapshot"""
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float


class SystemMonitor:
    """
    Monitors system resources and provides system information
    
    Features:
    - CPU, memory, disk monitoring
    - Network statistics
    - Process information
    - System information
    - Historical metrics tracking
    """
    
    def __init__(self, history_size: int = 100):
        """
        Initialize System Monitor
        
        Args:
            history_size: Number of historical metrics to keep
        """
        self.history_size = history_size
        self.metrics_history: List[SystemMetrics] = []
        
        # Get initial network counters
        self._initial_net_io = psutil.net_io_counters()
        
        logger.info(f"SystemMonitor initialized with history_size={history_size}")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Get CPU information
        
        Returns:
            Dictionary with CPU details
        """
        logger.info("Getting CPU information")
        
        try:
            cpu_freq = psutil.cpu_freq()
            
            info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'current_freq_mhz': cpu_freq.current if cpu_freq else None,
                'min_freq_mhz': cpu_freq.min if cpu_freq else None,
                'max_freq_mhz': cpu_freq.max if cpu_freq else None,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'per_cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
                'architecture': platform.machine(),
                'processor': platform.processor()
            }
            
            logger.success(f"CPU: {info['logical_cores']} cores, {info['cpu_percent']}% usage")
            return info
            
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {'error': str(e)}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get memory information
        
        Returns:
            Dictionary with memory details
        """
        logger.info("Getting memory information")
        
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = {
                'total_mb': mem.total / 1024 / 1024,
                'available_mb': mem.available / 1024 / 1024,
                'used_mb': mem.used / 1024 / 1024,
                'percent': mem.percent,
                'swap_total_mb': swap.total / 1024 / 1024,
                'swap_used_mb': swap.used / 1024 / 1024,
                'swap_percent': swap.percent
            }
            
            logger.success(f"Memory: {info['used_mb']:.0f}/{info['total_mb']:.0f} MB ({info['percent']}%)")
            return info
            
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}
    
    def get_disk_info(self, path: str = '/') -> Dict[str, Any]:
        """
        Get disk information
        
        Args:
            path: Path to check disk usage for (default: root)
            
        Returns:
            Dictionary with disk details
        """
        logger.info(f"Getting disk information for: {path}")
        
        try:
            # Adjust path for Windows
            if platform.system() == 'Windows' and path == '/':
                path = 'C:\\'
            
            usage = psutil.disk_usage(path)
            
            info = {
                'path': path,
                'total_gb': usage.total / 1024 / 1024 / 1024,
                'used_gb': usage.used / 1024 / 1024 / 1024,
                'free_gb': usage.free / 1024 / 1024 / 1024,
                'percent': usage.percent
            }
            
            logger.success(f"Disk: {info['used_gb']:.1f}/{info['total_gb']:.1f} GB ({info['percent']}%)")
            return info
            
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return {'error': str(e)}
    
    def get_all_disks_info(self) -> List[Dict[str, Any]]:
        """
        Get information for all disk partitions
        
        Returns:
            List of disk information dictionaries
        """
        logger.info("Getting all disks information")
        
        try:
            disks = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': usage.total / 1024 / 1024 / 1024,
                        'used_gb': usage.used / 1024 / 1024 / 1024,
                        'free_gb': usage.free / 1024 / 1024 / 1024,
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            
            logger.success(f"Found {len(disks)} disk partitions")
            return disks
            
        except Exception as e:
            logger.error(f"Error getting all disks info: {e}")
            return [{'error': str(e)}]
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information
        
        Returns:
            Dictionary with network details
        """
        logger.info("Getting network information")
        
        try:
            net_io = psutil.net_io_counters()
            
            # Calculate delta from initial
            sent_mb = (net_io.bytes_sent - self._initial_net_io.bytes_sent) / 1024 / 1024
            recv_mb = (net_io.bytes_recv - self._initial_net_io.bytes_recv) / 1024 / 1024
            
            info = {
                'bytes_sent_mb': net_io.bytes_sent / 1024 / 1024,
                'bytes_recv_mb': net_io.bytes_recv / 1024 / 1024,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drops_in': net_io.dropin,
                'drops_out': net_io.dropout,
                'session_sent_mb': sent_mb,
                'session_recv_mb': recv_mb
            }
            
            logger.success(f"Network: Sent {sent_mb:.1f} MB, Recv {recv_mb:.1f} MB (this session)")
            return info
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {'error': str(e)}
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """
        Get network interface information
        
        Returns:
            Dictionary of network interfaces
        """
        logger.info("Getting network interfaces")
        
        try:
            interfaces = {}
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addr_list in addrs.items():
                interface_info = {
                    'addresses': [],
                    'is_up': stats[interface_name].isup if interface_name in stats else False,
                    'speed_mbps': stats[interface_name].speed if interface_name in stats else None
                }
                
                for addr in addr_list:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                interfaces[interface_name] = interface_info
            
            logger.success(f"Found {len(interfaces)} network interfaces")
            return interfaces
            
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            return {'error': str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get general system information
        
        Returns:
            Dictionary with system details
        """
        logger.info("Getting system information")
        
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = (datetime.now() - boot_time).total_seconds()
            
            info = {
                'system': platform.system(),
                'node_name': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': uptime_seconds,
                'uptime_hours': uptime_seconds / 3600
            }
            
            logger.success(f"System: {info['system']} {info['release']}, Uptime: {info['uptime_hours']:.1f}h")
            return info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    def get_current_metrics(self) -> SystemMetrics:
        """
        Get current system metrics snapshot
        
        Returns:
            SystemMetrics object
        """
        logger.debug("Getting current metrics")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            
            # Get disk usage for primary drive
            if platform.system() == 'Windows':
                disk = psutil.disk_usage('C:\\')
            else:
                disk = psutil.disk_usage('/')
            
            net_io = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=mem.percent,
                disk_percent=disk.percent,
                network_sent_mb=net_io.bytes_sent / 1024 / 1024,
                network_recv_mb=net_io.bytes_recv / 1024 / 1024
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            raise
    
    def get_metrics_history(self, limit: int = None) -> List[SystemMetrics]:
        """
        Get historical metrics
        
        Args:
            limit: Maximum number of metrics to return (None for all)
            
        Returns:
            List of SystemMetrics
        """
        if limit:
            return self.metrics_history[-limit:]
        return self.metrics_history.copy()
    
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[Dict[str, Any]]:
        """
        Get top processes by resource usage
        
        Args:
            limit: Number of processes to return
            sort_by: Sort criteria ('cpu', 'memory')
            
        Returns:
            List of process information dictionaries
        """
        logger.info(f"Getting top {limit} processes by {sort_by}")
        
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu_percent': info['cpu_percent'],
                        'memory_percent': info['memory_percent'],
                        'memory_mb': info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort processes
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            
            top_processes = processes[:limit]
            
            logger.success(f"Retrieved top {len(top_processes)} processes")
            return top_processes
            
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []
    
    def check_resource_thresholds(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        disk_threshold: float = 90.0
    ) -> Dict[str, Any]:
        """
        Check if resource usage exceeds thresholds
        
        Args:
            cpu_threshold: CPU usage threshold percentage
            memory_threshold: Memory usage threshold percentage
            disk_threshold: Disk usage threshold percentage
            
        Returns:
            Dictionary with threshold check results
        """
        logger.info("Checking resource thresholds")
        
        try:
            metrics = self.get_current_metrics()
            
            alerts = []
            
            if metrics.cpu_percent > cpu_threshold:
                alerts.append(f"CPU usage high: {metrics.cpu_percent}% (threshold: {cpu_threshold}%)")
            
            if metrics.memory_percent > memory_threshold:
                alerts.append(f"Memory usage high: {metrics.memory_percent}% (threshold: {memory_threshold}%)")
            
            if metrics.disk_percent > disk_threshold:
                alerts.append(f"Disk usage high: {metrics.disk_percent}% (threshold: {disk_threshold}%)")
            
            result = {
                'cpu_ok': metrics.cpu_percent <= cpu_threshold,
                'memory_ok': metrics.memory_percent <= memory_threshold,
                'disk_ok': metrics.disk_percent <= disk_threshold,
                'all_ok': len(alerts) == 0,
                'alerts': alerts,
                'metrics': metrics.dict()
            }
            
            if alerts:
                logger.warning(f"Resource threshold alerts: {', '.join(alerts)}")
            else:
                logger.success("All resources within thresholds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
            return {'error': str(e)}
