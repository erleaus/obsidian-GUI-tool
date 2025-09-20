#!/usr/bin/env python3
"""
Quick test for summarization fixes - specifically to check if verses issue is resolved
"""

import os
import tempfile
from obsidian_ai_summarizer import ObsidianAISummarizer, SUMMARIZATION_AVAILABLE

def test_summarization_fixes():
    print("🧪 Testing Summarization Fixes")
    print("=" * 40)
    
    if not SUMMARIZATION_AVAILABLE:
        print("❌ Summarization not available")
        return False
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as test_dir:
        # Create .obsidian directory
        obsidian_dir = os.path.join(test_dir, ".obsidian")
        os.makedirs(obsidian_dir, exist_ok=True)
        
        # Create test content that might trigger verse-like output
        test_cases = [
            {
                "name": "Religious-style text",
                "content": """
                # Chapter 1: Introduction
                
                1. In the beginning was the concept of artificial intelligence
                2. And it was good for processing data
                3. Machine learning algorithms were created to understand patterns
                4. Deep neural networks emerged from this foundation
                
                Verse 1:1 - The fundamental principle is that AI systems learn from data.
                Verse 1:2 - They identify patterns and make predictions.
                
                ## Chapter 2: Applications
                
                1. Natural language processing
                2. Computer vision
                3. Robotics and automation
                """
            },
            {
                "name": "Numbered list content",
                "content": """
                # Meeting Notes
                
                1. Discussion of project timeline
                2. Review of budget constraints  
                3. Assignment of team responsibilities
                4. Planning next milestone
                
                Action items:
                1. Complete research phase by Friday
                2. Submit preliminary report
                3. Schedule follow-up meeting
                """
            },
            {
                "name": "Regular academic text",
                "content": """
                # Understanding Neural Networks
                
                Neural networks are computational models inspired by biological neural networks.
                They consist of interconnected nodes or neurons that process information.
                
                These systems learn through training on large datasets, adjusting connection
                weights to minimize prediction errors. Deep learning uses multiple hidden
                layers to model complex patterns in data.
                
                Applications include image recognition, natural language processing, and
                autonomous systems. The field continues to evolve rapidly with new
                architectures and training methods.
                """
            }
        ]
        
        # Initialize summarizer
        summarizer = ObsidianAISummarizer(test_dir)
        
        print("🔧 Loading model...")
        if not summarizer.load_model():
            print("❌ Failed to load model")
            return False
        
        print("✅ Model loaded successfully")
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['name']}")
            print("-" * 30)
            
            # Test text cleaning
            cleaned = summarizer.clean_text_for_summarization(test_case['content'])
            print(f"🧹 Cleaned text preview: {cleaned[:150]}...")
            
            # Test summarization
            try:
                result = summarizer.summarize_text(test_case['content'], 'auto')
                
                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                    continue
                
                summary = result['summary']
                print(f"📄 Summary: {summary}")
                
                # Analyze the result for verse-like patterns
                issues = []
                if any(pattern in summary.lower() for pattern in ['verse', 'chapter', '1.', '2.', '3.']):
                    issues.append("Contains verse/list patterns")
                if ':' in summary and any(c.isdigit() for c in summary):
                    if re.search(r'\d+:\d+', summary):
                        issues.append("Contains verse references (e.g., 1:2)")
                
                if issues:
                    print(f"⚠️ Issues found: {', '.join(issues)}")
                else:
                    print("✅ Summary looks good - no verse-like patterns detected")
                
                # Check quality
                if len(summary) < 50:
                    print("⚠️ Summary seems too short")
                elif len(summary) > 500:
                    print("⚠️ Summary seems too long")
                else:
                    print("✅ Summary length is appropriate")
                    
            except Exception as e:
                print(f"❌ Summarization failed: {e}")
        
        print(f"\n🎉 Testing completed!")
        return True

if __name__ == "__main__":
    import re
    test_summarization_fixes()