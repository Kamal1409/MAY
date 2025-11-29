"""
Example usage of Child Agent

This script demonstrates how to use the Child Agent to perform
various laptop operations.
"""

import asyncio
from agents.child_agent import ChildAgent
from agents.base_agent import AgentAction


async def main():
    """Main example function"""
    
    # Initialize Child Agent
    print("=" * 60)
    print("MAY Child Agent - Example Usage")
    print("=" * 60)
    print()
    
    agent = ChildAgent(
        name="ExampleAgent",
        allowed_paths=["E:\\MAY\\tests"],  # Only allow operations in tests directory
        enable_safety_checks=True
    )
    
    # Initialize agent
    await agent.initialize()
    
    # Get agent capabilities
    print("Agent Capabilities:")
    capabilities = agent.get_capabilities()
    print(f"  Name: {capabilities['name']}")
    print(f"  Status: {capabilities['status']}")
    print(f"  Safety Checks: {capabilities['safety_checks_enabled']}")
    print()
    
    # Example 1: Get system information
    print("Example 1: Getting System Information")
    print("-" * 60)
    
    action = AgentAction(
        action_id="action_001",
        action_type="get_system_info",
        parameters={}
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  System: {result.result['system']}")
        print(f"  Node: {result.result['node_name']}")
        print(f"  Uptime: {result.result['uptime_hours']:.1f} hours")
    else:
        print(f"  Error: {result.error}")
    print()
    
    # Example 2: Get CPU information
    print("Example 2: Getting CPU Information")
    print("-" * 60)
    
    action = AgentAction(
        action_id="action_002",
        action_type="get_cpu_info",
        parameters={}
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  Cores: {result.result['logical_cores']}")
        print(f"  CPU Usage: {result.result['cpu_percent']}%")
    else:
        print(f"  Error: {result.error}")
    print()
    
    # Example 3: Get memory information
    print("Example 3: Getting Memory Information")
    print("-" * 60)
    
    action = AgentAction(
        action_id="action_003",
        action_type="get_memory_info",
        parameters={}
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  Total: {result.result['total_mb']:.0f} MB")
        print(f"  Used: {result.result['used_mb']:.0f} MB")
        print(f"  Usage: {result.result['percent']}%")
    else:
        print(f"  Error: {result.error}")
    print()
    
    # Example 4: Check resource thresholds
    print("Example 4: Checking Resource Thresholds")
    print("-" * 60)
    
    action = AgentAction(
        action_id="action_004",
        action_type="check_resource_thresholds",
        parameters={
            'cpu_threshold': 80.0,
            'memory_threshold': 80.0,
            'disk_threshold': 90.0
        }
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  All OK: {result.result['all_ok']}")
        if result.result['alerts']:
            print("  Alerts:")
            for alert in result.result['alerts']:
                print(f"    - {alert}")
    else:
        print(f"  Error: {result.error}")
    print()
    
    # Example 5: List processes
    print("Example 5: Listing Top Processes by CPU")
    print("-" * 60)
    
    action = AgentAction(
        action_id="action_005",
        action_type="get_top_processes",
        parameters={'limit': 5, 'sort_by': 'cpu'}
    )
    
    result = await agent.execute_action(action)
    if result.success:
        for i, proc in enumerate(result.result, 1):
            print(f"  {i}. {proc['name']} (PID: {proc['pid']})")
            print(f"     CPU: {proc['cpu_percent']}%, Memory: {proc['memory_mb']:.1f} MB")
    else:
        print(f"  Error: {result.error}")
    print()
    
    # Example 6: File operations (in allowed directory)
    print("Example 6: File Operations")
    print("-" * 60)
    
    # Write a test file
    action = AgentAction(
        action_id="action_006",
        action_type="write_file",
        parameters={
            'file_path': 'E:\\MAY\\tests\\example_file.txt',
            'content': 'Hello from MAY Child Agent!',
            'overwrite': True
        }
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  ✓ File written successfully")
        print(f"    Size: {result.result['size_bytes']} bytes")
    else:
        print(f"  ✗ Error: {result.error}")
    
    # Read the file back
    action = AgentAction(
        action_id="action_007",
        action_type="read_file",
        parameters={'file_path': 'E:\\MAY\\tests\\example_file.txt'}
    )
    
    result = await agent.execute_action(action)
    if result.success:
        print(f"  ✓ File read successfully")
        print(f"    Content: {result.result['content']}")
    else:
        print(f"  ✗ Error: {result.error}")
    print()
    
    # Get action history
    print("Action History:")
    print("-" * 60)
    history = agent.get_action_history(limit=5)
    for action_result in history:
        status = "✓" if action_result.success else "✗"
        print(f"  {status} {action_result.action_id}: {action_result.execution_time:.3f}s")
    print()
    
    # Shutdown agent
    await agent.shutdown()
    
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
