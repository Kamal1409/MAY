"""
MAY Agent System Initializer

This script initializes and runs the MAY agent system for local development.
It sets up the child agent and provides an interactive interface to test operations.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from agents.child_agent import ChildAgent
from agents.base_agent import AgentAction

# Load environment variables
load_dotenv()


class MAYSystem:
    """Main MAY agent system controller"""
    
    def __init__(self):
        self.child_agent = None
        self.running = False
        
    async def initialize(self):
        """Initialize the MAY agent system"""
        print("=" * 70)
        print("MAY - Multi-Agent AI System")
        print("=" * 70)
        print()
        
        # Initialize Child Agent
        print("Initializing Child Agent...")
        self.child_agent = ChildAgent(
            name="MAY-ChildAgent",
            allowed_paths=[
                str(Path.cwd()),  # Current directory
                str(Path.cwd() / "tests"),  # Tests directory
                str(Path.cwd() / "data"),  # Data directory
            ],
            enable_safety_checks=True
        )
        
        await self.child_agent.initialize()
        print("[OK] Child Agent initialized successfully")
        print()
        
        # Display capabilities
        capabilities = self.child_agent.get_capabilities()
        print(f"Agent Name: {capabilities['name']}")
        print(f"Status: {capabilities['status']}")
        print(f"Safety Checks: {capabilities['safety_checks_enabled']}")
        print()
        
        self.running = True
        
    async def get_system_status(self):
        """Get current system status"""
        print("\n" + "=" * 70)
        print("System Status")
        print("=" * 70)
        
        # System Info
        action = AgentAction(
            action_id="status_001",
            action_type="get_system_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"\nSystem: {result.result['system']}")
            print(f"Node: {result.result['node_name']}")
            print(f"Uptime: {result.result['uptime_hours']:.1f} hours")
        
        # CPU Info
        action = AgentAction(
            action_id="status_002",
            action_type="get_cpu_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"\nCPU Cores: {result.result['logical_cores']}")
            print(f"CPU Usage: {result.result['cpu_percent']}%")
        
        # Memory Info
        action = AgentAction(
            action_id="status_003",
            action_type="get_memory_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"\nMemory Total: {result.result['total_mb']:.0f} MB")
            print(f"Memory Used: {result.result['used_mb']:.0f} MB")
            print(f"Memory Usage: {result.result['percent']}%")
        
        print("=" * 70)
        
    async def interactive_mode(self):
        """Run interactive command mode"""
        print("\n" + "=" * 70)
        print("Interactive Mode - Available Commands:")
        print("=" * 70)
        print("  status  - Show system status")
        print("  cpu     - Show CPU information")
        print("  memory  - Show memory information")
        print("  disk    - Show disk information")
        print("  procs   - Show top processes")
        print("  test    - Run a test file operation")
        print("  quit    - Exit the system")
        print("=" * 70)
        print()
        
        while self.running:
            try:
                command = input("\nMAY> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    await self.get_system_status()
                elif command == "cpu":
                    await self._show_cpu_info()
                elif command == "memory":
                    await self._show_memory_info()
                elif command == "disk":
                    await self._show_disk_info()
                elif command == "procs":
                    await self._show_top_processes()
                elif command == "test":
                    await self._test_file_operations()
                elif command == "":
                    continue
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def _show_cpu_info(self):
        """Show CPU information"""
        action = AgentAction(
            action_id="cpu_info",
            action_type="get_cpu_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"\nPhysical Cores: {result.result['physical_cores']}")
            print(f"Logical Cores: {result.result['logical_cores']}")
            print(f"CPU Usage: {result.result['cpu_percent']}%")
            print(f"Per-Core Usage: {result.result['per_cpu_percent']}")
        else:
            print(f"Error: {result.error}")
    
    async def _show_memory_info(self):
        """Show memory information"""
        action = AgentAction(
            action_id="mem_info",
            action_type="get_memory_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"\nTotal: {result.result['total_mb']:.0f} MB")
            print(f"Available: {result.result['available_mb']:.0f} MB")
            print(f"Used: {result.result['used_mb']:.0f} MB")
            print(f"Usage: {result.result['percent']}%")
        else:
            print(f"Error: {result.error}")
    
    async def _show_disk_info(self):
        """Show disk information for all partitions"""
        action = AgentAction(
            action_id="disk_info",
            action_type="get_all_disks_info",
            parameters={}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print("\nDisk Partitions:")
            print("-" * 70)
            for disk in result.result:
                if 'error' not in disk:
                    print(f"\n{disk['device']} -> {disk['mountpoint']}")
                    print(f"  Type: {disk['fstype']}")
                    print(f"  Total: {disk['total_gb']:.1f} GB")
                    print(f"  Used:  {disk['used_gb']:.1f} GB ({disk['percent']}%)")
                    print(f"  Free:  {disk['free_gb']:.1f} GB")
        else:
            print(f"Error: {result.error}")
    
    async def _show_top_processes(self):
        """Show top processes"""
        action = AgentAction(
            action_id="top_procs",
            action_type="get_top_processes",
            parameters={'limit': 10, 'sort_by': 'cpu'}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print("\nTop 10 Processes by CPU:")
            print("-" * 70)
            for i, proc in enumerate(result.result, 1):
                print(f"{i:2}. {proc['name']:<30} PID: {proc['pid']:<8} CPU: {proc['cpu_percent']:>5}%  MEM: {proc['memory_mb']:>8.1f} MB")
        else:
            print(f"Error: {result.error}")
    
    async def _test_file_operations(self):
        """Test file operations"""
        test_file = Path.cwd() / "tests" / "may_test.txt"
        
        print(f"\nTesting file operations with: {test_file}")
        
        # Write file
        action = AgentAction(
            action_id="test_write",
            action_type="write_file",
            parameters={
                'file_path': str(test_file),
                'content': f'MAY Agent Test - {asyncio.get_event_loop().time()}',
                'overwrite': True
            }
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"[OK] File written: {result.result['size_bytes']} bytes")
        else:
            print(f"[FAIL] Write failed: {result.error}")
            return
        
        # Read file
        action = AgentAction(
            action_id="test_read",
            action_type="read_file",
            parameters={'file_path': str(test_file)}
        )
        result = await self.child_agent.execute_action(action)
        
        if result.success:
            print(f"[OK] File read: {result.result['content']}")
        else:
            print(f"[FAIL] Read failed: {result.error}")
    
    async def shutdown(self):
        """Shutdown the MAY system"""
        print("\n" + "=" * 70)
        print("Shutting down MAY system...")
        
        if self.child_agent:
            # Show action history
            history = self.child_agent.get_action_history(limit=10)
            print(f"\nExecuted {len(history)} actions in this session:")
            for action_result in history[-5:]:
                status = "[OK]" if action_result.success else "[FAIL]"
                print(f"  {status} {action_result.action_id}: {action_result.execution_time:.3f}s")
            
            await self.child_agent.shutdown()
            print("[OK] Child Agent shutdown complete")
        
        print("\nMAY system shutdown complete")
        print("=" * 70)
        self.running = False


async def main():
    """Main entry point"""
    system = MAYSystem()
    
    try:
        # Initialize system
        await system.initialize()
        
        # Show initial status
        await system.get_system_status()
        
        # Run interactive mode
        await system.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always shutdown gracefully
        await system.shutdown()


if __name__ == "__main__":
    print("\nStarting MAY Agent System...")
    print("Press Ctrl+C to exit\n")
    asyncio.run(main())
