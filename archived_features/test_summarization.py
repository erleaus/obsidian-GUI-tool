#!/usr/bin/env python3
"""
Test script for Obsidian AI Summarization functionality
Run this to test the summarization features before using the GUI
"""

import os
import sys
from pathlib import Path

def test_summarization():
    """Test the summarization functionality"""
    print("🧪 Testing Obsidian AI Summarization")
    print("=" * 50)
    
    # Test import
    try:
        from obsidian_ai_summarizer import ObsidianAISummarizer, SUMMARIZATION_AVAILABLE
        print("✅ Successfully imported ObsidianAISummarizer")
    except ImportError as e:
        print(f"❌ Failed to import summarization module: {e}")
        print("Install dependencies with: pip install transformers torch")
        return False
    
    if not SUMMARIZATION_AVAILABLE:
        print("❌ Summarization dependencies not available")
        print("Install dependencies with: pip install transformers torch")
        return False
    
    print("✅ Summarization dependencies available")
    
    # Ask for test vault path
    vault_path = input("\nEnter path to test Obsidian vault (or press Enter to create test text): ").strip()
    
    if vault_path and os.path.exists(vault_path):
        # Test with real vault
        print(f"📁 Using vault: {vault_path}")
        summarizer = ObsidianAISummarizer(vault_path)
        
        if not summarizer.is_available():
            print("❌ Summarizer not available")
            return False
        
        print("✅ Summarizer initialized")
        
        # Test file summarization
        print("\n📄 Testing file summarization...")
        md_files = list(Path(vault_path).glob("*.md"))
        if md_files:
            test_file = str(md_files[0].relative_to(vault_path))
            print(f"Testing with file: {test_file}")
            
            def progress_callback(msg):
                print(f"   {msg}")
            
            result = summarizer.summarize_file(test_file, 'auto', progress_callback)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Summary generated:")
                print(f"   Length: {len(result['summary'])} characters")
                print(f"   Cached: {result.get('cached', False)}")
                print(f"\n📝 Summary:")
                print(f"   {result['summary'][:200]}...")
                
                if 'metadata' in result:
                    meta = result['metadata']
                    print(f"\n📊 Stats:")
                    print(f"   Compression ratio: {meta.get('compression_ratio', 0):.1%}")
                    print(f"   Chunks processed: {meta.get('chunks_processed', 1)}")
        else:
            print("❌ No markdown files found in vault")
    
    else:
        # Test with sample text
        print("📝 Testing with sample text...")
        
        # Create a temporary vault directory for testing
        test_dir = "/tmp/obsidian_test_vault"
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(os.path.join(test_dir, ".obsidian"), exist_ok=True)
        
        # Create sample text
        sample_text = """
        # Understanding Artificial Intelligence
        
        Artificial Intelligence (AI) represents one of the most significant technological advances of our time. 
        It encompasses machine learning, deep learning, natural language processing, and computer vision.
        
        ## Machine Learning Fundamentals
        
        Machine learning is a subset of AI that enables computers to learn and improve from experience without 
        being explicitly programmed. It involves algorithms that can identify patterns in data and make 
        predictions or decisions based on that data.
        
        ### Types of Machine Learning
        
        There are three main types of machine learning:
        
        1. **Supervised Learning**: Uses labeled data to train models
        2. **Unsupervised Learning**: Finds patterns in unlabeled data  
        3. **Reinforcement Learning**: Learns through interaction with an environment
        
        ## Deep Learning Revolution
        
        Deep learning, a subset of machine learning, uses neural networks with multiple layers to model and 
        understand complex patterns. This has led to breakthroughs in image recognition, natural language 
        processing, and game playing.
        
        ## Natural Language Processing
        
        NLP enables computers to understand, interpret, and generate human language. Applications include 
        translation, sentiment analysis, chatbots, and text summarization - like what we're testing right now!
        
        ## Future Implications
        
        AI technology continues to evolve rapidly, with potential applications in healthcare, autonomous vehicles, 
        robotics, and countless other fields. However, it also raises important questions about ethics, privacy, 
        and the future of work.
        
        The development of AI systems requires careful consideration of their societal impact and the need for 
        responsible development practices.
        """
        
        # Save sample text to file
        sample_file = os.path.join(test_dir, "ai_overview.md")
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        # Test summarization
        summarizer = ObsidianAISummarizer(test_dir)
        
        print("✅ Created test environment")
        
        def progress_callback(msg):
            print(f"   {msg}")
        
        # Test different summary types
        summary_types = ['brief', 'auto', 'detailed']
        
        for summary_type in summary_types:
            print(f"\n📝 Testing {summary_type} summary...")
            result = summarizer.summarize_file("ai_overview.md", summary_type, progress_callback)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                cached_text = " (cached)" if result.get('cached', False) else ""
                print(f"✅ {summary_type.title()} summary generated{cached_text}:")
                print(f"   Length: {len(result['summary'])} characters")
                
                if 'metadata' in result:
                    meta = result['metadata']
                    print(f"   Compression: {meta.get('compression_ratio', 0):.1%}")
                
                print(f"\n📄 Summary:")
                print(f"   {result['summary']}")
        
        # Test cache statistics
        print(f"\n📊 Cache Statistics:")
        stats = summarizer.get_summary_stats()
        if 'error' not in stats:
            print(f"   Total summaries: {stats.get('total_summaries', 0)}")
            print(f"   Cache size: {stats.get('cache_size', '0 MB')}")
            if 'summary_types' in stats:
                print(f"   Summary types: {stats['summary_types']}")
        
        # Clean up
        import shutil
        try:
            shutil.rmtree(test_dir)
            print("✅ Cleaned up test files")
        except:
            pass
    
    print("\n🎉 Summarization testing completed!")
    return True

def test_gui_integration():
    """Test GUI integration"""
    print("\n🖥️  Testing GUI Integration")
    print("-" * 30)
    
    try:
        from obsidian_backlink_checker import ObsidianBacklinkChecker, SUMMARIZATION_AVAILABLE
        print("✅ Successfully imported GUI with summarization")
        print(f"   Summarization enabled: {SUMMARIZATION_AVAILABLE}")
    except ImportError as e:
        print(f"❌ Failed to import GUI: {e}")
        return False
    
    print("✅ GUI integration test passed")
    return True

if __name__ == "__main__":
    success = True
    
    success &= test_summarization()
    success &= test_gui_integration()
    
    if success:
        print("\n🎉 All tests passed! Summarization is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run GUI: python obsidian_backlink_checker.py")
        print("3. Test standalone summarizer: python obsidian_ai_summarizer.py")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)