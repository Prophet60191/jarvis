#!/usr/bin/env python3
"""
Debug the aider integration to identify why code generation is failing.
"""

import sys
import subprocess
import os
from pathlib import Path
sys.path.append('jarvis')

def debug_aider_integration():
    """Debug aider integration issues."""
    
    print("🔍 DEBUGGING AIDER INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Check if aider command is available
        print("\n🧪 TEST 1: AIDER COMMAND AVAILABILITY")
        print("-" * 40)
        
        try:
            result = subprocess.run(["aider", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Aider is installed: {result.stdout.strip()}")
            else:
                print(f"❌ Aider command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Aider command timed out")
        except FileNotFoundError:
            print("❌ Aider command not found")
        except Exception as e:
            print(f"❌ Aider command error: {e}")
        
        # Test 2: Test aider integration function directly
        print("\n🧪 TEST 2: AIDER INTEGRATION FUNCTION")
        print("-" * 40)
        
        try:
            from jarvis.tools.plugins.aider_integration import aider_code_edit
            
            print("✅ Aider integration imported successfully")
            
            # Create a test directory
            test_dir = Path("./test_aider_debug")
            test_dir.mkdir(exist_ok=True)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(test_dir)
            
            print(f"📁 Test directory: {test_dir.absolute()}")
            
            # Test simple aider call
            test_prompt = """
            Create a simple Python file called 'hello.py' that prints "Hello, World!".
            
            The file should:
            - Have a main function
            - Include proper comments
            - Follow Python best practices
            """
            
            print("🧪 Testing aider with simple prompt...")
            result = aider_code_edit(test_prompt)
            
            print(f"✅ Aider function completed")
            print(f"📄 Result length: {len(result)} characters")
            print(f"📋 Result preview:")
            print("-" * 30)
            print(result[:500] + "..." if len(result) > 500 else result)
            
            # Check if files were created
            created_files = list(Path(".").glob("*.py"))
            print(f"\n📁 Files created: {len(created_files)}")
            for file in created_files:
                print(f"   📄 {file.name} ({file.stat().st_size} bytes)")
                
                # Show file content
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                    print(f"   📝 Content preview:")
                    print(f"   {content[:200]}...")
                except Exception as e:
                    print(f"   ⚠️  Could not read file: {e}")
            
            # Clean up
            os.chdir(original_cwd)
            
            # Remove test files
            for file in test_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            test_dir.rmdir()
            
        except Exception as e:
            print(f"❌ Aider integration test failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Make sure we're back in original directory
            try:
                os.chdir(original_cwd)
            except:
                pass
        
        # Test 3: Check aider configuration
        print("\n🧪 TEST 3: AIDER CONFIGURATION")
        print("-" * 40)
        
        try:
            # Test aider with specific model
            result = subprocess.run([
                "aider", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Aider help command works")
                
                # Check for model options
                if "ollama" in result.stdout.lower():
                    print("✅ Ollama support detected")
                else:
                    print("⚠️  Ollama support not clearly indicated")
                    
            else:
                print(f"❌ Aider help failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Aider configuration test failed: {e}")
        
        # Test 4: Check Ollama connectivity
        print("\n🧪 TEST 4: OLLAMA CONNECTIVITY")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                "curl", "-s", "http://localhost:11434/api/tags"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Ollama server is responding")
                print(f"📋 Available models: {result.stdout[:200]}...")
            else:
                print("❌ Ollama server not responding")
                
        except Exception as e:
            print(f"⚠️  Could not test Ollama: {e}")
        
        # Test 5: Check environment variables
        print("\n🧪 TEST 5: ENVIRONMENT VARIABLES")
        print("-" * 40)
        
        env_vars = [
            "AIDER_NO_GIT",
            "AIDER_NO_AUTO_COMMIT", 
            "AIDER_NO_BROWSER",
            "AIDER_NONINTERACTIVE",
            "OLLAMA_API_BASE"
        ]
        
        for var in env_vars:
            value = os.environ.get(var, "Not set")
            print(f"   {var}: {value}")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 AIDER INTEGRATION DEBUG RESULTS:")
    print("=" * 50)
    print("🔍 Check the test results above to identify:")
    print("   1. Whether aider command is working")
    print("   2. If aider integration function executes")
    print("   3. Whether files are actually created")
    print("   4. If Ollama connectivity is working")
    print("   5. Environment variable configuration")
    
    print(f"\n💡 COMMON ISSUES:")
    print("1. Aider not finding the correct model")
    print("2. Ollama server not running")
    print("3. Environment variables not set correctly")
    print("4. Aider hanging in interactive mode")
    print("5. File permissions or directory issues")

if __name__ == "__main__":
    debug_aider_integration()
