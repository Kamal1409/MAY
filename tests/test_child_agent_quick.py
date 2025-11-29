"""
Quick test script for Child Agent - Core functionality only
Tests only the modules that don't require external dependencies
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.child_agent import ChildAgent
from agents.base_agent import AgentAction


async def test_child_agent():
    """Test Child Agent basic functionality"""
    
    print("=" * 70)
    print("MAY Child Agent - Quick Functionality Test")
    print("=" * 70)
    print()
    
    try:
        # Initialize Child Agent
        print("1. Initializing Child Agent...")
        agent = ChildAgent(
            name="TestAgent",
        )
        
        success = await agent.initialize()
        if success:
            print("✓ Agent initialized successfully")
        else:
            print("✗ Agent initialization failed")
            return False
        print()
        
        # Test 1: Get capabilities
        print("2. Testing get_capabilities()...")
        capabilities = agent.get_capabilities()
        print(f"✓ Agent Name: {capabilities['name']}")
        print(f"✓ Agent Type: {capabilities['type']}")
        print(f"✓ Status: {capabilities['status']}")
        print(f"✓ File Operations: {len(capabilities['capabilities']['file_operations'])} available")
        print(f"✓ App Operations: {len(capabilities['capabilities']['application_operations'])} available")
        print(f"✓ System Monitoring: {len(capabilities['capabilities']['system_monitoring'])} available")
        print()
        
        # Test 2: System Info
        print("3. Testing get_system_info()...")
        action = AgentAction(
            action_id="test_001",
            action_type="get_system_info",
            parameters={}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ System: {result.result['system']}")
            print(f"✓ Node: {result.result['node_name']}")
            print(f"✓ Python: {result.result['python_version']}")
            print(f"✓ Uptime: {result.result['uptime_hours']:.2f} hours")
            print(f"✓ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Test 3: CPU Info
        print("4. Testing get_cpu_info()...")
        action = AgentAction(
            action_id="test_002",
            action_type="get_cpu_info",
            parameters={}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ Physical Cores: {result.result['physical_cores']}")
            print(f"✓ Logical Cores: {result.result['logical_cores']}")
            print(f"✓ CPU Usage: {result.result['cpu_percent']:.1f}%")
            print(f"✓ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Test 4: Memory Info
        print("5. Testing get_memory_info()...")
        action = AgentAction(
            action_id="test_003",
            action_type="get_memory_info",
            parameters={}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ Total Memory: {result.result['total_mb']:.0f} MB")
            print(f"✓ Used Memory: {result.result['used_mb']:.0f} MB")
            print(f"✓ Memory Usage: {result.result['percent']:.1f}%")
            print(f"✓ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Test 5: Disk Info
        print("6. Testing get_disk_info()...")
        action = AgentAction(
            action_id="test_004",
            action_type="get_disk_info",
            parameters={}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ Total Disk: {result.result['total_gb']:.1f} GB")
            print(f"✓ Used Disk: {result.result['used_gb']:.1f} GB")
            print(f"✓ Disk Usage: {result.result['percent']:.1f}%")
            print(f"✓ Execution time: {result.execution_time:.3f}s")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Test 6: File Operations
        print("7. Testing file operations...")
        test_file = os.path.join(os.path.dirname(__file__), "test_output.txt")
        
        # Write file
        action = AgentAction(
            action_id="test_005",
            action_type="write_file",
            parameters={
                'file_path': test_file,
                'content': 'Hello from MAY Child Agent!\nThis is a test file.',
                'overwrite': True
            }
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ File written: {result.result['size_bytes']} bytes")
        else:
            print(f"✗ Write failed: {result.error}")
            return False
        
        # Read file
        action = AgentAction(
            action_id="test_006",
            action_type="read_file",
            parameters={'file_path': test_file}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ File read: {result.result['size_bytes']} bytes")
            print(f"✓ Content preview: {result.result['content'][:50]}...")
        else:
            print(f"✗ Read failed: {result.error}")
            return False
        
        # Get file info
        action = AgentAction(
            action_id="test_007",
            action_type="get_file_info",
            parameters={'file_path': test_file}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ File info retrieved")
            print(f"  Name: {result.result['name']}")
            print(f"  Size: {result.result['size_bytes']} bytes")
        else:
            print(f"✗ Info failed: {result.error}")
            return False
        
        # Delete file
        action = AgentAction(
            action_id="test_008",
            action_type="delete_file",
            parameters={'file_path': test_file, 'confirm': True}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ File deleted successfully")
        else:
            print(f"✗ Delete failed: {result.error}")
            return False
        print()
        
        # Test 7: List processes
        print("8. Testing list_processes()...")
        action = AgentAction(
            action_id="test_009",
            action_type="list_processes",
            parameters={'filter_name': 'python'}
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ Found {result.result['count']} Python processes")
            if result.result['processes']:
                proc = result.result['processes'][0]
                print(f"✓ Example: {proc['name']} (PID: {proc['pid']})")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Test 8: Check resource thresholds
        print("9. Testing check_resource_thresholds()...")
        action = AgentAction(
            action_id="test_010",
            action_type="check_resource_thresholds",
            parameters={
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'disk_threshold': 90
            }
        )
        result = await agent.execute_action(action)
        
        if result.success:
            print(f"✓ Resource check completed")
            print(f"  CPU OK: {result.result['cpu_ok']}")
            print(f"  Memory OK: {result.result['memory_ok']}")
            print(f"  Disk OK: {result.result['disk_ok']}")
        else:
            print(f"✗ Error: {result.error}")
            return False
        print()
        
        # Final summary
        print("=" * 70)
        print("✓ All tests passed successfully!")
        print("=" * 70)
        
        # Cleanup
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_child_agent())
    sys.exit(0 if success else 1)
