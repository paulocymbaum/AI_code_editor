"""
Test Enhanced AI Agent with Detailed Logging
"""
import asyncio
from src.agent_core import setup_logging, AICodeAgent

async def main():
    print('🚀 Starting AI Code Agent with Enhanced Logging...\n')
    
    # Setup logging
    log_file = setup_logging('agent_detailed.log')
    print(f'📝 Logging to: {log_file}\n')
    
    agent = AICodeAgent()
    
    # Simple test task
    result = await agent.execute("""
Create a simple React dashboard with:
1. A header with title "My Dashboard"
2. One StatCard component showing "Total Users: 1,234"
3. Professional styling with Tailwind CSS

Generate ALL files needed for a Next.js app in the demo/ directory.
""")
    
    print('\n' + '='*80)
    print('📊 EXECUTION SUMMARY')
    print('='*80)
    print(f'Success: {result["success"]}')
    print(f'Iterations: {result.get("iterations", 0)}')
    print(f'Tools called: {len(result.get("actions_taken", []))}')
    
    if result['success']:
        print('\n✅ Task completed successfully!')
        print('\nGenerated files:')
        import os
        for root, dirs, files in os.walk('demo'):
            for file in files:
                if file.endswith(('.tsx', '.ts', '.css', '.json')):
                    print(f'  - {os.path.join(root, file)}')
    else:
        print(f'\n❌ Task failed: {result.get("error", "Unknown error")}')
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
