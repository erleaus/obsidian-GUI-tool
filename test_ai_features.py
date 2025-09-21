#!/usr/bin/env python3
"""
AI Features Testing Script
Comprehensive tests for the Obsidian AI functionality
"""

import os
import sys
import tempfile
import shutil
import numpy as np
from pathlib import Path
from typing import Dict, List

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def create_test_vault() -> str:
    """Create a temporary Obsidian vault for testing"""
    vault_path = tempfile.mkdtemp(prefix="obsidian_test_")
    
    # Create .obsidian directory
    obsidian_dir = os.path.join(vault_path, ".obsidian")
    os.makedirs(obsidian_dir)
    
    # Create test markdown files
    test_files = {
        "Machine Learning.md": """# Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms.

## Neural Networks
Neural networks are inspired by biological neurons and form the backbone of deep learning.

## Applications
- Image recognition
- Natural language processing
- Predictive analytics

Related: [[Artificial Intelligence]], [[Data Science]]
""",
        
        "Artificial Intelligence.md": """# Artificial Intelligence

AI is the simulation of human intelligence in machines.

## History
The field of AI was founded in 1956 at Dartmouth College.

## Subfields
- Machine learning
- Natural language processing  
- Computer vision
- Robotics

See also: [[Machine Learning]], [[Deep Learning]]
""",
        
        "Data Science.md": """# Data Science

Data science combines statistics, programming, and domain expertise.

## Process
1. Data collection
2. Data cleaning
3. Exploratory analysis
4. Modeling
5. Visualization

## Tools
- Python
- R
- SQL
- Jupyter notebooks

Links: [[Machine Learning]], [[Statistics]]
""",
        
        "Deep Learning.md": """# Deep Learning

Deep learning uses neural networks with multiple layers.

## Architecture Types
- Convolutional Neural Networks (CNNs)
- Recurrent Neural Networks (RNNs)  
- Transformer models

## Applications
- Computer vision
- Speech recognition
- Language translation

Connect to: [[Machine Learning]], [[Neural Networks]]
""",
        
        "Statistics.md": """# Statistics

Statistics is the study of data collection, analysis, and interpretation.

## Branches
- Descriptive statistics
- Inferential statistics
- Bayesian statistics

## Key Concepts
- Probability distributions
- Hypothesis testing
- Regression analysis

Related topics: [[Data Science]], [[Probability]]
"""
    }
    
    # Write test files
    for filename, content in test_files.items():
        file_path = os.path.join(vault_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return vault_path


def test_ai_imports():
    """Test AI library imports"""
    print("🧪 Testing AI library imports...")
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        import numpy as np
        import pickle
        print("✅ All AI libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_ai_model_loading():
    """Test AI model loading and basic functionality"""
    print("🧪 Testing AI model loading...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Test default model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Default model loaded successfully")
        
        # Test embedding creation
        test_texts = [
            "This is about machine learning and artificial intelligence.",
            "Data science involves statistics and programming.",
            "Neural networks are used in deep learning applications."
        ]
        
        embeddings = model.encode(test_texts)
        print(f"✅ Embeddings created: shape {embeddings.shape}")
        
        # Test similarity calculation
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(embeddings)
        print(f"✅ Similarity matrix calculated: shape {similarities.shape}")
        
        return True, model, embeddings
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False, None, None


def test_obsidian_ai_search():
    """Test ObsidianAISearch class functionality"""
    print("🧪 Testing ObsidianAISearch functionality...")
    
    vault_path = None
    try:
        # Import the AI search class
        from obsidian_ai_search import ObsidianAISearch
        
        # Create test vault
        vault_path = create_test_vault()
        print(f"✅ Test vault created: {vault_path}")
        
        # Initialize AI search
        ai_search = ObsidianAISearch(vault_path)
        
        if not ai_search.is_available():
            print("❌ AI search not available")
            return False
        
        print("✅ AI search initialized")
        
        # Test index building
        print("   Building AI index...")
        success = ai_search.build_index()
        if not success:
            print("❌ Index building failed")
            return False
        
        print("✅ AI index built successfully")
        
        # Test semantic search
        print("   Testing semantic search...")
        results = ai_search.semantic_search("machine learning algorithms", top_k=3)
        
        if not results:
            print("❌ No search results returned")
            return False
        
        print(f"✅ Semantic search returned {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"   {i}. {result['file']} (similarity: {result['similarity']:.3f})")
        
        # Test similar files functionality
        print("   Testing similar files search...")
        similar_results = ai_search.find_similar_to_file("Machine Learning.md", top_k=3)
        
        if similar_results:
            print(f"✅ Similar files search returned {len(similar_results)} results")
            for i, result in enumerate(similar_results[:2], 1):
                print(f"   {i}. {result['file']} (similarity: {result['similarity']:.3f})")
        else:
            print("⚠️  No similar files found")
        
        # Test caching
        print("   Testing cache functionality...")
        ai_search.save_cache()
        
        # Create new instance and load cache
        ai_search2 = ObsidianAISearch(vault_path)
        cache_loaded = ai_search2.load_cache()
        
        if cache_loaded:
            print("✅ Cache saved and loaded successfully")
        else:
            print("⚠️  Cache functionality has issues")
        
        return True
        
    except Exception as e:
        print(f"❌ ObsidianAISearch test failed: {e}")
        return False
    finally:
        # Cleanup
        if vault_path and os.path.exists(vault_path):
            shutil.rmtree(vault_path)


def test_gui_ai_integration():
    """Test AI integration in the GUI (without actually showing GUI)"""
    print("🧪 Testing GUI AI integration...")
    
    try:
        import tkinter as tk
        from obsidian_backlink_checker import ObsidianBacklinkChecker
        
        # Create root window (hidden)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize the checker
        app = ObsidianBacklinkChecker(root)
        
        # Check if AI is enabled
        if not app.ai_search_enabled:
            print("❌ AI search not enabled in GUI")
            return False
        
        print("✅ AI search enabled in GUI")
        
        # Test AI components exist
        if not hasattr(app, 'ai_model'):
            print("❌ AI model attribute missing")
            return False
        
        if not hasattr(app, 'ai_embeddings'):
            print("❌ AI embeddings attribute missing")
            return False
        
        if not hasattr(app, 'ai_documents'):
            print("❌ AI documents attribute missing")
            return False
        
        print("✅ All AI attributes present in GUI")
        
        # Test AI configuration variables
        config_vars = ['ai_similarity_threshold', 'ai_model_var', 'batch_processing', 'max_results_var']
        for var in config_vars:
            if hasattr(app, var):
                print(f"✅ Configuration variable {var} present")
            else:
                print(f"⚠️  Configuration variable {var} missing")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI AI integration test failed: {e}")
        return False


def test_ai_performance():
    """Test AI performance with various scenarios"""
    print("🧪 Testing AI performance...")
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import time
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test small dataset performance
        small_texts = ["Test document " + str(i) for i in range(10)]
        start_time = time.time()
        small_embeddings = model.encode(small_texts)
        small_time = time.time() - start_time
        print(f"✅ Small dataset (10 docs): {small_time:.2f}s")
        
        # Test medium dataset performance
        medium_texts = ["Test document with more content " + str(i) * 10 for i in range(100)]
        start_time = time.time()
        medium_embeddings = model.encode(medium_texts)
        medium_time = time.time() - start_time
        print(f"✅ Medium dataset (100 docs): {medium_time:.2f}s")
        
        # Test similarity computation performance
        start_time = time.time()
        similarities = cosine_similarity(medium_embeddings[:10], medium_embeddings)
        sim_time = time.time() - start_time
        print(f"✅ Similarity computation: {sim_time:.3f}s")
        
        # Test memory usage (approximate)
        import sys
        embedding_size = sys.getsizeof(medium_embeddings)
        print(f"✅ Embedding memory usage: ~{embedding_size / (1024*1024):.1f} MB for 100 documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def run_all_tests():
    """Run all AI feature tests"""
    print("🚀 Starting comprehensive AI feature tests...\n")
    
    tests = [
        ("AI Imports", test_ai_imports),
        ("AI Model Loading", lambda: test_ai_model_loading()[0]),
        ("ObsidianAISearch", test_obsidian_ai_search),
        ("GUI Integration", test_gui_ai_integration),
        ("Performance", test_ai_performance)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI features are working correctly!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)