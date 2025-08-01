#!/usr/bin/env python3
"""
Test script for the unified coding workflow with real plugin integration.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add jarvis to path
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

from jarvis.core.agent import JarvisAgent
from jarvis.config import LLMConfig

async def test_unified_workflow():
    print('🚀 Testing Unified Coding Workflow with Real Plugins')
    print('=' * 60)
    
    # Clean up any existing files
    import os
    files_to_clean = ['index.html', 'style.css', 'script.js', 'hello.html']
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f'🗑️ Cleaned up {file}')
    
    # Create Jarvis agent
    config = LLMConfig()
    agent = JarvisAgent(config)
    agent.initialize(tools=[])
    
    # Test request
    request = 'Create a simple HTML page that shows Hello World'
    
    print(f'\n🎯 Request: {request}')
    print('🔧 This will test the complete unified workflow:')
    print('  • Real Aider plugin for code generation')
    print('  • Real Open Interpreter plugin for testing')
    print('  • Actual file creation and validation')
    print()
    
    try:
        # Execute the unified workflow
        response = await agent.process_input(request)
        
        print('📝 Jarvis Response:')
        print('=' * 50)
        print(response[:800])
        if len(response) > 800:
            print('...')
        print('=' * 50)
        
        # Check results
        if '🎉 **Unified Coding Workflow Complete!**' in response:
            print('\n🎉 SUCCESS: Unified workflow completed!')
            
            # Check for generated files
            files_found = []
            for file in files_to_clean:
                if os.path.exists(file):
                    files_found.append(file)
                    print(f'✅ {file} - CREATED')
            
            if files_found:
                print(f'\n🎯 SUCCESS: {len(files_found)} files generated!')
                
                # Show content of first file
                first_file = files_found[0]
                print(f'\n📄 Content of {first_file}:')
                with open(first_file, 'r') as f:
                    content = f.read()
                    print(content)
                
                # Check if it's real content
                if 'Hello World' in content or 'hello world' in content.lower():
                    print('\n🎉 REAL CONTENT GENERATED!')
                    print('✅ The unified coding workflow is working perfectly!')
                elif 'Placeholder' in content:
                    print('\n⚠️ Only placeholder content - Aider needs configuration')
                else:
                    print('\n📝 Content generated - checking quality...')
                    
            else:
                print('\n❌ No files were generated')
                
        else:
            print('\n📝 Different response received')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n🎯 Unified Workflow Test Complete!')

if __name__ == "__main__":
    asyncio.run(test_unified_workflow())
