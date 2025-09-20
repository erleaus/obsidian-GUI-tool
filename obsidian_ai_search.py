#!/usr/bin/env python3
"""
Obsidian AI Semantic Search - Prototype
Adds AI-powered conceptual search to the Obsidian Checker
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import re

# These would need to be installed:
# pip install sentence-transformers numpy scikit-learn

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI dependencies not installed. Run:")
    print("   pip install sentence-transformers numpy scikit-learn")


class ObsidianAISearch:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.embeddings_cache = {}
        self.documents = []
        self.embeddings = None
        self.model = None
        
        if AI_AVAILABLE:
            # Using a lightweight, fast model that runs locally
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
        self.cache_file = os.path.join(vault_path, '.obsidian', 'ai_search_cache.pkl')
        
    def is_available(self) -> bool:
        """Check if AI search is available"""
        return AI_AVAILABLE and self.model is not None
    
    def extract_content_chunks(self, file_path: Path) -> List[Dict]:
        """Extract meaningful chunks from markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = []
            
            # Split by headers and paragraphs
            sections = re.split(r'\n(?=#{1,6}\s)', content)
            
            for i, section in enumerate(sections):
                if section.strip():
                    # Clean up markdown formatting for better embedding
                    clean_text = self.clean_markdown(section)
                    if len(clean_text.strip()) > 50:  # Skip very short sections
                        chunks.append({
                            'file': str(file_path.relative_to(self.vault_path)),
                            'content': clean_text,
                            'section': i,
                            'preview': clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
                        })
            
            # If no headers, split by paragraphs
            if len(chunks) == 0:
                paragraphs = content.split('\n\n')
                for i, para in enumerate(paragraphs):
                    clean_para = self.clean_markdown(para)
                    if len(clean_para.strip()) > 50:
                        chunks.append({
                            'file': str(file_path.relative_to(self.vault_path)),
                            'content': clean_para,
                            'section': i,
                            'preview': clean_para[:200] + "..." if len(clean_para) > 200 else clean_para
                        })
            
            return chunks
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
    
    def clean_markdown(self, text: str) -> str:
        """Clean markdown formatting for better embedding"""
        # Remove markdown formatting but keep the content
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # Wiki links
        text = re.sub(r'[#*_`]', '', text)  # Formatting chars
        text = re.sub(r'\n+', ' ', text)  # Multiple newlines
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        return text.strip()
    
    def build_index(self) -> bool:
        """Build semantic search index for the vault"""
        if not self.is_available():
            return False
            
        print("🤖 Building AI semantic index...")
        print("   This may take a few minutes for large vaults...")
        
        try:
            # Find all markdown files
            md_files = list(Path(self.vault_path).rglob("*.md"))
            
            # Extract content chunks
            all_chunks = []
            for i, md_file in enumerate(md_files):
                if i % 10 == 0:
                    print(f"   Processing file {i+1}/{len(md_files)}: {md_file.name}")
                
                chunks = self.extract_content_chunks(md_file)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                print("❌ No content found to index")
                return False
            
            print(f"   Creating embeddings for {len(all_chunks)} content chunks...")
            
            # Create embeddings
            texts = [chunk['content'] for chunk in all_chunks]
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Store everything
            self.documents = all_chunks
            self.embeddings = embeddings
            
            # Cache the results
            self.save_cache()
            
            print(f"✅ AI index built successfully!")
            print(f"   Indexed {len(all_chunks)} chunks from {len(md_files)} files")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def load_cache(self) -> bool:
        """Load cached embeddings if available"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.documents = cache_data['documents']
                    self.embeddings = cache_data['embeddings']
                print(f"✅ Loaded cached AI index ({len(self.documents)} chunks)")
                return True
            except Exception as e:
                print(f"⚠️  Error loading cache: {e}")
        return False
    
    def save_cache(self):
        """Save embeddings to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            cache_data = {
                'documents': self.documents,
                'embeddings': self.embeddings
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print("💾 AI index cached for future use")
        except Exception as e:
            print(f"⚠️  Error saving cache: {e}")
    
    def semantic_search(self, query: str, top_k: int = 10, min_similarity: float = 0.3) -> List[Dict]:
        """Perform semantic search for concepts"""
        if not self.is_available() or self.embeddings is None:
            return []
        
        try:
            # Create query embedding
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top results above threshold
            results = []
            for i, similarity in enumerate(similarities):
                if similarity >= min_similarity:
                    result = self.documents[i].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Error during semantic search: {e}")
            return []
    
    def find_similar_to_file(self, file_path: str, top_k: int = 5) -> List[Dict]:
        """Find files similar to a given file"""
        if not self.is_available() or self.embeddings is None:
            return []
        
        try:
            # Find chunks from the target file
            target_chunks = [doc for doc in self.documents if doc['file'] == file_path]
            if not target_chunks:
                return []
            
            # Average the embeddings for the target file
            target_indices = [i for i, doc in enumerate(self.documents) if doc['file'] == file_path]
            target_embedding = np.mean([self.embeddings[i] for i in target_indices], axis=0)
            
            # Find similar chunks from other files
            similarities = cosine_similarity([target_embedding], self.embeddings)[0]
            
            results = []
            seen_files = {file_path}  # Don't include the target file itself
            
            for i, similarity in enumerate(similarities):
                if similarity > 0.3 and self.documents[i]['file'] not in seen_files:
                    result = self.documents[i].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
                    seen_files.add(result['file'])
            
            # Sort and limit
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Error finding similar files: {e}")
            return []


def demo_ai_search():
    """Demo function to show AI search capabilities"""
    vault_path = input("Enter path to your Obsidian vault: ").strip()
    
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Invalid vault path")
        return
    
    ai_search = ObsidianAISearch(vault_path)
    
    if not ai_search.is_available():
        print("❌ AI search not available. Install dependencies first.")
        return
    
    # Try to load cache, otherwise build index
    if not ai_search.load_cache():
        if not ai_search.build_index():
            return
    
    print("\n🎉 AI Search Ready!")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. 🔍 Semantic search")
        print("2. 📄 Find similar files")
        print("3. 🔄 Rebuild index")
        print("4. 🚪 Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            query = input("Enter conceptual search query: ").strip()
            if query:
                print(f"\n🤖 Searching for concept: '{query}'...")
                results = ai_search.semantic_search(query)
                
                if results:
                    print(f"\n✅ Found {len(results)} conceptually related chunks:")
                    print("-" * 60)
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. 📄 {result['file']} (similarity: {result['similarity']:.2f})")
                        print(f"   {result['preview']}")
                else:
                    print("❌ No conceptually related content found")
        
        elif choice == "2":
            file_path = input("Enter relative file path (e.g., notes/example.md): ").strip()
            if file_path:
                print(f"\n🤖 Finding files similar to '{file_path}'...")
                results = ai_search.find_similar_to_file(file_path)
                
                if results:
                    print(f"\n✅ Found {len(results)} similar files:")
                    print("-" * 60)
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. 📄 {result['file']} (similarity: {result['similarity']:.2f})")
                        print(f"   {result['preview']}")
                else:
                    print("❌ No similar files found")
        
        elif choice == "3":
            ai_search.build_index()
        
        elif choice == "4":
            break
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    demo_ai_search()