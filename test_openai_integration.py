#!/usr/bin/env python3
"""
Test script for OpenAI integration
Tests each component without requiring real API keys
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from openai_client import OpenAIClient, OpenAIClientError
        print("✅ OpenAI client module imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI client import failed: {e}")
        return False
    
    try:
        from obsidian_conversation import ObsidianConversation
        print("✅ Conversation module imported successfully")
    except ImportError as e:
        print(f"❌ Conversation module import failed: {e}")
        return False
    
    try:
        from obsidian_ai_search import ObsidianAISearch
        print("✅ AI search module imported successfully")
    except ImportError as e:
        print(f"❌ AI search module import failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("\n🧪 Testing dependencies...")
    
    missing_deps = []
    
    try:
        import openai
        print("✅ openai package available")
    except ImportError:
        missing_deps.append("openai")
        print("❌ openai package not found")
    
    try:
        import tiktoken
        print("✅ tiktoken package available")
    except ImportError:
        missing_deps.append("tiktoken")
        print("❌ tiktoken package not found")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv package available")
    except ImportError:
        missing_deps.append("python-dotenv")
        print("❌ python-dotenv package not found")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers package available")
    except ImportError:
        print("⚠️ sentence-transformers package not found (optional for local AI)")
    
    if missing_deps:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("Run: pip install " + " ".join(missing_deps))
        return False
    
    return True

def test_openai_client():
    """Test OpenAI client initialization (without API key)"""
    print("\n🧪 Testing OpenAI client initialization...")
    
    from openai_client import OpenAIClient, OpenAIClientError
    
    # Test without API key (should fail gracefully)
    try:
        client = OpenAIClient()
        print("❌ OpenAI client initialized without API key (unexpected)")
        return False
    except OpenAIClientError as e:
        if "API key not found" in str(e):
            print("✅ OpenAI client correctly requires API key")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_conversation_module():
    """Test conversation module initialization"""
    print("\n🧪 Testing conversation module...")
    
    from obsidian_conversation import ObsidianConversation
    
    # Create a temporary test directory
    test_vault = Path("/tmp/test_vault")
    test_vault.mkdir(exist_ok=True)
    obsidian_dir = test_vault / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)
    
    try:
        conversation = ObsidianConversation(str(test_vault))
        print("✅ Conversation module initialized successfully")
        
        # Test availability check
        available = conversation.is_available()
        print(f"✅ Availability check: {available} (expected False without API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation module error: {e}")
        return False
    finally:
        # Cleanup
        import shutil
        if test_vault.exists():
            shutil.rmtree(test_vault)

def test_cli_integration():
    """Test that CLI can import all modules"""
    print("\n🧪 Testing CLI integration...")
    
    # Test that the CLI script can be imported
    try:
        import obsidian_checker_cli
        print("✅ CLI script imported successfully")
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False
    
    return True

def test_env_template():
    """Test that environment template exists and is valid"""
    print("\n🧪 Testing environment template...")
    
    env_template = Path(".env.template")
    if not env_template.exists():
        print("❌ .env.template file not found")
        return False
    
    print("✅ .env.template file exists")
    
    # Check that it contains required keys
    required_keys = [
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_TEMPERATURE",
        "MAX_CONTEXT_CHUNKS",
        "SIMILARITY_THRESHOLD"
    ]
    
    content = env_template.read_text()
    missing_keys = [key for key in required_keys if key not in content]
    
    if missing_keys:
        print(f"❌ Missing keys in .env.template: {missing_keys}")
        return False
    
    print("✅ .env.template contains all required keys")
    return True

def main():
    """Run all tests"""
    print("🚀 OpenAI Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("OpenAI Client", test_openai_client),
        ("Conversation Module", test_conversation_module),
        ("CLI Integration", test_cli_integration),
        ("Environment Template", test_env_template),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! OpenAI integration is ready.")
        print("\nNext steps:")
        print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("2. Copy .env.template to .env and add your API key")
        print("3. Test with: python3 obsidian_checker_cli.py --ask 'Hello' --vault /path/to/vault")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before using OpenAI integration.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)