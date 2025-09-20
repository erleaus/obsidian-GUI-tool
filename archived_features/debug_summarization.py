#!/usr/bin/env python3
"""
Debug script for summarization issues
This will help identify why summaries are giving verses instead of proper summaries
"""

import os
import sys
from obsidian_ai_summarizer import ObsidianAISummarizer, SUMMARIZATION_AVAILABLE

def debug_summarization():
    print("🔍 Debug: AI Summarization Issues")
    print("=" * 50)
    
    if not SUMMARIZATION_AVAILABLE:
        print("❌ Summarization not available - install dependencies first")
        return
    
    # Get vault path
    vault_path = input("Enter your Obsidian vault path: ").strip()
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Invalid vault path")
        return
    
    # Get file to test
    file_path = input("Enter file path to debug (e.g., notes/example.md): ").strip()
    
    try:
        # Initialize summarizer
        print("\n🔧 Initializing summarizer...")
        summarizer = ObsidianAISummarizer(vault_path, model_name='distilbart')
        
        # Read the file content
        full_path = os.path.join(vault_path, file_path)
        if not os.path.exists(full_path):
            print(f"❌ File not found: {full_path}")
            return
            
        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        print(f"\n📄 Original content length: {len(original_content)} characters")
        print(f"📄 First 200 chars: {original_content[:200]}...")
        
        # Debug text cleaning
        print("\n🧹 Testing text cleaning...")
        cleaned_content = summarizer.clean_text_for_summarization(original_content)
        print(f"📄 Cleaned content length: {len(cleaned_content)} characters")
        print(f"📄 First 200 chars after cleaning: {cleaned_content[:200]}...")
        
        # Debug chunking
        print("\n📦 Testing text chunking...")
        chunks = summarizer.chunk_text(original_content)
        print(f"📄 Number of chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"📄 Chunk {i+1} length: {len(chunk)} chars, words: {len(chunk.split())}")
            print(f"📄 Chunk {i+1} preview: {chunk[:150]}...")
            if i >= 2:  # Only show first 3 chunks
                break
        
        # Test direct pipeline call with debugging
        print("\n🤖 Loading model and testing pipeline...")
        
        def progress_callback(msg):
            print(f"   {msg}")
        
        # Load model
        if not summarizer.load_model(progress_callback):
            print("❌ Failed to load model")
            return
        
        print("\n🧪 Testing direct summarization with different parameters...")
        
        # Test with minimal text first
        test_text = """
        Artificial intelligence is a branch of computer science that aims to create machines 
        that can perform tasks that typically require human intelligence. These tasks include 
        learning, reasoning, problem-solving, perception, and language understanding. Modern AI 
        systems use machine learning algorithms to analyze large amounts of data and make 
        predictions or decisions based on patterns they discover.
        """
        
        print(f"🧪 Testing with controlled text ({len(test_text)} chars)...")
        
        # Try different parameters
        test_configs = [
            {'max_length': 50, 'min_length': 10, 'do_sample': False},
            {'max_length': 100, 'min_length': 20, 'do_sample': True, 'temperature': 0.7},
            {'max_length': 130, 'min_length': 30, 'do_sample': False, 'early_stopping': True},
        ]
        
        for i, config in enumerate(test_configs):
            print(f"\n🔬 Test {i+1} with config: {config}")
            try:
                result = summarizer.summarizer(test_text.strip(), **config)
                summary = result[0]['summary_text']
                print(f"✅ Result: {summary}")
                print(f"📊 Length: {len(summary)} chars")
                
                # Check if result looks like verses or lists
                if '1.' in summary or '2.' in summary or summary.count('\n') > 3:
                    print("⚠️ WARNING: Result looks like a list/verses!")
                elif len(summary.split('.')) > 5:
                    print("⚠️ WARNING: Result might be fragmented!")
                else:
                    print("✅ Result looks like a proper summary")
                    
            except Exception as e:
                print(f"❌ Test {i+1} failed: {e}")
        
        # Now test with actual file content
        print(f"\n🧪 Testing with your actual file content...")
        
        # Use first chunk if file is large
        test_chunk = chunks[0] if chunks else cleaned_content
        if len(test_chunk) > 1000:
            test_chunk = test_chunk[:1000]  # Limit for testing
            
        print(f"📄 Testing chunk length: {len(test_chunk)} chars")
        
        try:
            result = summarizer.summarizer(
                test_chunk,
                max_length=130,
                min_length=30,
                do_sample=False,
                truncation=True
            )
            summary = result[0]['summary_text']
            print(f"✅ Your file summary: {summary}")
            
            # Analyze the result
            print(f"\n🔍 Analysis:")
            print(f"   Summary length: {len(summary)} chars")
            print(f"   Number of sentences: {len(summary.split('.'))}")
            print(f"   Contains numbers: {'Yes' if any(c.isdigit() for c in summary) else 'No'}")
            print(f"   Contains verse patterns: {'Yes' if any(pattern in summary for pattern in ['1.', '2.', ':', 'verse', 'chapter']) else 'No'}")
            
            if 'verse' in summary.lower() or 'chapter' in summary.lower():
                print("⚠️ ISSUE FOUND: The model thinks your content is religious text!")
                print("💡 SOLUTION: This might be because your content has numbered sections or biblical-style formatting")
                print("💡 Try preprocessing to remove verse numbers or chapter markers")
            
        except Exception as e:
            print(f"❌ Failed to summarize your content: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def check_settings_button():
    print("\n🔧 Checking for settings buttons...")
    
    # Check the GUI file for any settings-related code
    try:
        with open("/Users/ericaustin/obsidian-GUI-tool/obsidian_backlink_checker.py", 'r') as f:
            content = f.read()
            
        # Look for settings-related code
        if 'settings' in content.lower():
            lines = content.split('\n')
            settings_lines = [f"Line {i+1}: {line}" for i, line in enumerate(lines) if 'settings' in line.lower()]
            
            print("🔍 Found settings-related code:")
            for line in settings_lines:
                print(f"   {line}")
        else:
            print("ℹ️ No settings button found in the current GUI code")
            
    except Exception as e:
        print(f"❌ Error checking settings: {e}")

if __name__ == "__main__":
    debug_summarization()
    check_settings_button()