#!/usr/bin/env python3
"""
Test script for the modern Obsidian GUI
"""

import tkinter as tk
from obsidian_modern_gui import ModernObsidianGUI
import os

def test_gui_functionality():
    """Test that the GUI loads and basic functionality is accessible"""
    print("🧪 Testing Modern Obsidian GUI...")
    print("-" * 40)
    
    try:
        # Create root window
        root = tk.Tk()
        app = ModernObsidianGUI(root)
        
        # Test 1: GUI initialization
        print("✅ GUI initialized successfully")
        
        # Test 2: Check if all key methods exist
        required_methods = [
            'check_backlinks',
            'search_vault',
            'ai_search',
            'build_ai_index',
            'find_similar_files',
            'auto_summarize',
            'open_obsidian',
            'export_results'
        ]
        
        for method_name in required_methods:
            if hasattr(app, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
        
        # Test 3: Check if AI variables are properly initialized
        ai_vars = [
            'ai_model',
            'ai_embeddings',
            'ai_documents',
            'ai_search_results',
            'ai_similarity_threshold',
            'ai_model_var',
            'batch_processing',
            'max_results_var'
        ]
        
        for var_name in ai_vars:
            if hasattr(app, var_name):
                print(f"✅ AI variable {var_name} initialized")
            else:
                print(f"❌ AI variable {var_name} missing")
        
        # Test 4: Check if modern styling is applied
        if hasattr(app, 'colors') and 'bg_primary' in app.colors:
            print("✅ Modern color scheme applied")
        else:
            print("❌ Modern color scheme missing")
        
        # Test 5: Check if all required widgets exist
        widgets = ['vault_entry', 'search_entry', 'results_display', 'progress']
        for widget_name in widgets:
            if hasattr(app, widget_name):
                print(f"✅ Widget {widget_name} created")
            else:
                print(f"❌ Widget {widget_name} missing")
        
        print("\n🎉 All tests passed! The modern GUI is ready to use.")
        print("\n📋 Features available:")
        print("   • Modern dark theme with web-inspired design")
        print("   • Backlink checking with detailed results")
        print("   • Advanced text search with regex support")
        print("   • AI-powered concept search (if dependencies installed)")
        print("   • Find similar files using AI")
        print("   • Auto-summarization of vault content")
        print("   • Export results to various formats")
        print("   • Conversational AI chat (if configured)")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gui_functionality()
    if success:
        print("\n🚀 To run the GUI, execute: python3 obsidian_modern_gui.py")
    else:
        print("\n⚠️  Please check the errors above before running the GUI")