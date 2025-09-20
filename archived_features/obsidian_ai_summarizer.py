#!/usr/bin/env python3
"""
Obsidian AI Summarization Module
Provides local text summarization capabilities for Obsidian vaults using BART/DistilBART models
"""

import os
import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime

# Check for summarization dependencies
try:
    from transformers import (
        BartForConditionalGeneration, 
        BartTokenizer,
        AutoTokenizer, 
        AutoModelForSeq2SeqLM,
        pipeline
    )
    import torch
    SUMMARIZATION_AVAILABLE = True
except ImportError:
    SUMMARIZATION_AVAILABLE = False
    print("⚠️  Summarization dependencies not installed. Run:")
    print("   pip install transformers torch")


class ObsidianAISummarizer:
    """Local AI text summarization for Obsidian vault content"""
    
    # Model options (ordered by quality vs speed trade-off)
    MODELS = {
        'distilbart': {
            'name': 'sshleifer/distilbart-cnn-12-6',
            'description': 'Fast, lightweight summarization (~268MB)',
            'max_length': 1024,
            'recommended': True
        },
        'bart-large': {
            'name': 'facebook/bart-large-cnn',
            'description': 'High-quality summarization (~1.6GB)',
            'max_length': 1024,
            'recommended': False
        },
        'flan-t5-small': {
            'name': 'google/flan-t5-small',
            'description': 'Very fast, smaller model (~80MB)',
            'max_length': 512,
            'recommended': False
        }
    }
    
    def __init__(self, vault_path: str, model_name: str = 'distilbart'):
        self.vault_path = vault_path
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.summarizer = None
        self.cache_dir = os.path.join(vault_path, '.obsidian', 'ai_summaries')
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Model configuration
        self.model_config = self.MODELS.get(model_name, self.MODELS['distilbart'])
        self.max_input_length = self.model_config['max_length']
        
    def is_available(self) -> bool:
        """Check if summarization is available"""
        return SUMMARIZATION_AVAILABLE
    
    def load_model(self, progress_callback=None) -> bool:
        """Load the summarization model"""
        if not self.is_available():
            return False
            
        try:
            if progress_callback:
                progress_callback("Loading tokenizer...")
            
            model_name = self.model_config['name']
            
            # Load model and tokenizer
            if 'flan-t5' in model_name:
                # T5 models use AutoTokenizer and AutoModelForSeq2SeqLM
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                if progress_callback:
                    progress_callback("Loading model...")
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            else:
                # BART models
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                if progress_callback:
                    progress_callback("Loading model...")
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Create pipeline for easier usage
            if progress_callback:
                progress_callback("Creating summarization pipeline...")
            
            self.summarizer = pipeline(
                "summarization", 
                model=self.model, 
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1  # Use GPU if available
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading summarization model: {e}")
            return False
    
    def get_content_hash(self, content: str) -> str:
        """Generate hash for content to use as cache key"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_cached_summary(self, content: str, summary_type: str = 'auto') -> Optional[Dict]:
        """Get cached summary if available"""
        content_hash = self.get_content_hash(content)
        cache_file = os.path.join(self.cache_dir, f"{content_hash}_{summary_type}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Check if cache is recent (within 30 days)
                    cache_date = datetime.fromisoformat(cached_data.get('created_at', ''))
                    if (datetime.now() - cache_date).days < 30:
                        return cached_data
            except Exception as e:
                print(f"Warning: Error loading cache: {e}")
        return None
    
    def save_summary_to_cache(self, content: str, summary: str, summary_type: str = 'auto', metadata: Dict = None):
        """Save summary to cache"""
        try:
            content_hash = self.get_content_hash(content)
            cache_file = os.path.join(self.cache_dir, f"{content_hash}_{summary_type}.json")
            
            cache_data = {
                'summary': summary,
                'summary_type': summary_type,
                'model_used': self.model_name,
                'created_at': datetime.now().isoformat(),
                'content_length': len(content),
                'summary_length': len(summary),
                'metadata': metadata or {}
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Error saving to cache: {e}")
    
    def clean_text_for_summarization(self, text: str) -> str:
        """Clean and prepare text for summarization"""
        # Remove markdown headers but keep the text content
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # Remove # headers
        
        # Remove numbered lists and bullet points that might confuse the model
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Remove "1. " etc
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Remove bullet points
        
        # Remove verse-like patterns (common in religious/structured texts)
        text = re.sub(r'\b\d+:\d+\b', '', text)  # Remove verse references like "1:23"
        text = re.sub(r'\bverse\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bchapter\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace and formatting
        text = re.sub(r'\n+', ' ', text)  # Multiple newlines
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [text](url)
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # [[wikilink]]
        
        # Remove excessive markdown formatting
        text = re.sub(r'[#*_`]{2,}', '', text)  # Multiple formatting chars
        text = re.sub(r'[#*_`]', ' ', text)  # Single formatting chars
        
        # Remove code blocks
        text = re.sub(r'```[^`]*```', ' [CODE BLOCK] ', text)
        text = re.sub(r'`[^`]+`', ' [CODE] ', text)
        
        # Remove special characters that might confuse the model
        text = re.sub(r'[\[\]{}()]', '', text)
        
        # Ensure we have proper sentences
        text = re.sub(r'\s+', ' ', text)  # Clean up spaces again
        
        # Add context clue to help model understand this is regular text
        cleaned_text = text.strip()
        if cleaned_text and not cleaned_text.startswith('This document discusses'):
            cleaned_text = f"This document discusses: {cleaned_text}"
        
        return cleaned_text
    
    def chunk_text(self, text: str, max_chunk_size: int = 900) -> List[str]:
        """Split text into chunks that fit within model limits"""
        # Clean text first
        clean_text = self.clean_text_for_summarization(text)
        
        # If text is short enough, return as single chunk
        if len(clean_text.split()) <= max_chunk_size:
            return [clean_text]
        
        chunks = []
        sentences = re.split(r'[.!?]+', clean_text)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk.split()) <= max_chunk_size:
                current_chunk = potential_chunk
            else:
                # Start new chunk
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def post_process_summary(self, summary: str) -> str:
        """Post-process the summary to remove verse-like patterns and improve readability"""
        if not summary:
            return summary
            
        # Remove verse-like patterns that might have slipped through
        summary = re.sub(r'\b\d+:\d+\b', '', summary)  # Remove verse references
        summary = re.sub(r'^\s*\d+\.\s*', '', summary, flags=re.MULTILINE)  # Remove numbered list items
        summary = re.sub(r'^\s*[-*•]\s*', '', summary, flags=re.MULTILINE)  # Remove bullet points
        
        # Remove common verse-related words if they appear at the start
        summary = re.sub(r'^(verse|chapter|psalm)\s+\d+[:\s]*', '', summary, flags=re.IGNORECASE)
        
        # Clean up redundant phrases that might indicate confused generation
        summary = re.sub(r'\b(verse|chapter|psalm|bible|scripture)\b', '', summary, flags=re.IGNORECASE)
        
        # Fix sentence structure - ensure sentences flow naturally
        summary = re.sub(r'\s+', ' ', summary)  # Multiple spaces
        summary = re.sub(r'\s*\.\s*\.', '.', summary)  # Double periods
        summary = re.sub(r'\s*,\s*,', ',', summary)  # Double commas
        
        # Ensure the summary starts with a capital letter
        summary = summary.strip()
        if summary and summary[0].islower():
            summary = summary[0].upper() + summary[1:]
        
        # Remove any remaining "This document discusses:" prefix if redundant
        if summary.startswith('This document discusses: This document discusses:'):
            summary = summary.replace('This document discusses: This document discusses:', 'This document discusses:', 1)
        
        # Ensure proper sentence endings
        summary = summary.strip()
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
            
        return summary
    
    def summarize_text(self, text: str, summary_type: str = 'auto',
                      max_length: int = None, min_length: int = 30,
                      progress_callback=None) -> Dict:
        """
        Summarize text using local AI model
        
        Args:
            text: Text to summarize
            summary_type: Type of summary ('auto', 'brief', 'detailed', 'key_points')
            max_length: Maximum summary length
            min_length: Minimum summary length
            progress_callback: Function to call with progress updates
            
        Returns:
            Dict with summary and metadata
        """
        if not self.is_available() or not text.strip():
            return {'error': 'Summarization not available or empty text'}
        
        # Check cache first
        cached = self.get_cached_summary(text, summary_type)
        if cached:
            if progress_callback:
                progress_callback("Using cached summary...")
            return {
                'summary': cached['summary'],
                'cached': True,
                'metadata': cached.get('metadata', {})
            }
        
        # Load model if not loaded
        if self.summarizer is None:
            if progress_callback:
                progress_callback("Loading AI model...")
            if not self.load_model(progress_callback):
                return {'error': 'Failed to load summarization model'}
        
        try:
            # Set length parameters based on summary type
            if max_length is None:
                length_configs = {
                    'brief': {'max_length': 50, 'min_length': 20},
                    'auto': {'max_length': 130, 'min_length': 30},
                    'detailed': {'max_length': 300, 'min_length': 50},
                    'key_points': {'max_length': 200, 'min_length': 40}
                }
                config = length_configs.get(summary_type, length_configs['auto'])
                max_length = config['max_length']
                min_length = config['min_length']
            
            if progress_callback:
                progress_callback("Preparing text for summarization...")
            
            # Chunk text if too long
            chunks = self.chunk_text(text)
            
            if len(chunks) == 1:
                # Single chunk - direct summarization
                if progress_callback:
                    progress_callback("Generating summary...")
                
                result = self.summarizer(
                    chunks[0],
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=True,  # Enable sampling for more natural output
                    temperature=0.7,  # Add some randomness to avoid repetitive patterns
                    num_beams=4,  # Use beam search for better quality
                    early_stopping=True,
                    no_repeat_ngram_size=3,  # Prevent repetitive n-grams
                    repetition_penalty=1.2,  # Penalize repetition
                    truncation=True
                )
                summary = result[0]['summary_text']
                summary = self.post_process_summary(summary)
                
            else:
                # Multiple chunks - summarize each then combine
                if progress_callback:
                    progress_callback(f"Summarizing {len(chunks)} text chunks...")
                
                chunk_summaries = []
                for i, chunk in enumerate(chunks):
                    if progress_callback:
                        progress_callback(f"Processing chunk {i+1}/{len(chunks)}...")
                    
                    result = self.summarizer(
                        chunk,
                        max_length=min(max_length // len(chunks) + 20, 150),
                        min_length=min(min_length, 20),
                        do_sample=True,
                        temperature=0.7,
                        num_beams=4,
                        early_stopping=True,
                        no_repeat_ngram_size=3,
                        repetition_penalty=1.2,
                        truncation=True
                    )
                    chunk_summary = self.post_process_summary(result[0]['summary_text'])
                    chunk_summaries.append(chunk_summary)
                
                # Combine chunk summaries
                combined_text = ' '.join(chunk_summaries)
                
                if progress_callback:
                    progress_callback("Creating final summary...")
                
                # Final summarization of combined chunks
                if len(combined_text.split()) > max_length:
                    result = self.summarizer(
                        combined_text,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=True,
                        temperature=0.7,
                        num_beams=4,
                        early_stopping=True,
                        no_repeat_ngram_size=3,
                        repetition_penalty=1.2,
                        truncation=True
                    )
                    summary = self.post_process_summary(result[0]['summary_text'])
                else:
                    summary = combined_text
            
            # Create metadata
            metadata = {
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text) if text else 0,
                'chunks_processed': len(chunks),
                'model_used': self.model_name
            }
            
            # Cache the result
            self.save_summary_to_cache(text, summary, summary_type, metadata)
            
            if progress_callback:
                progress_callback("Summary complete!")
            
            return {
                'summary': summary,
                'cached': False,
                'metadata': metadata
            }
            
        except Exception as e:
            error_msg = f"Error during summarization: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def summarize_file(self, file_path: str, summary_type: str = 'auto', 
                      progress_callback=None) -> Dict:
        """Summarize a markdown file"""
        try:
            full_path = os.path.join(self.vault_path, file_path)
            if not os.path.exists(full_path):
                return {'error': f'File not found: {file_path}'}
            
            if progress_callback:
                progress_callback(f"Reading file: {file_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {'error': 'File is empty'}
            
            # Add file metadata
            result = self.summarize_text(content, summary_type, progress_callback=progress_callback)
            if 'metadata' in result:
                result['metadata']['file_path'] = file_path
                result['metadata']['file_size'] = len(content)
            
            return result
            
        except Exception as e:
            return {'error': f'Error reading file {file_path}: {str(e)}'}
    
    def summarize_search_results(self, search_results: List[Dict], 
                               summary_type: str = 'auto',
                               progress_callback=None) -> Dict:
        """Summarize content from search results"""
        if not search_results:
            return {'error': 'No search results to summarize'}
        
        try:
            # Combine content from search results
            combined_content = []
            file_list = []
            
            for result in search_results:
                if 'preview' in result:
                    combined_content.append(result['preview'])
                elif 'content' in result:
                    combined_content.append(result['content'])
                
                if 'file' in result:
                    file_list.append(result['file'])
            
            if not combined_content:
                return {'error': 'No content found in search results'}
            
            full_content = '\n\n'.join(combined_content)
            
            if progress_callback:
                progress_callback(f"Summarizing content from {len(search_results)} search results...")
            
            result = self.summarize_text(full_content, summary_type, progress_callback=progress_callback)
            
            # Add search result metadata
            if 'metadata' in result:
                result['metadata']['search_results_count'] = len(search_results)
                result['metadata']['files_included'] = file_list[:10]  # First 10 files
                result['metadata']['total_files'] = len(set(file_list))
            
            return result
            
        except Exception as e:
            return {'error': f'Error summarizing search results: {str(e)}'}
    
    def get_summary_stats(self) -> Dict:
        """Get statistics about cached summaries"""
        try:
            cache_files = list(Path(self.cache_dir).glob("*.json"))
            
            if not cache_files:
                return {'total_summaries': 0, 'cache_size': '0 MB'}
            
            total_size = sum(f.stat().st_size for f in cache_files)
            size_mb = total_size / (1024 * 1024)
            
            # Load some cache files to get more stats
            summary_types = {}
            models_used = {}
            
            for cache_file in cache_files[:50]:  # Sample first 50 files
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        summary_type = data.get('summary_type', 'unknown')
                        model = data.get('model_used', 'unknown')
                        summary_types[summary_type] = summary_types.get(summary_type, 0) + 1
                        models_used[model] = models_used.get(model, 0) + 1
                except:
                    continue
            
            return {
                'total_summaries': len(cache_files),
                'cache_size': f'{size_mb:.1f} MB',
                'summary_types': summary_types,
                'models_used': models_used
            }
            
        except Exception as e:
            return {'error': f'Error getting cache stats: {str(e)}'}
    
    def clear_cache(self) -> bool:
        """Clear the summary cache"""
        try:
            cache_files = list(Path(self.cache_dir).glob("*.json"))
            for cache_file in cache_files:
                cache_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False


def demo_summarizer():
    """Demo function to test summarization capabilities"""
    print("🤖 Obsidian AI Summarization Demo")
    print("=" * 50)
    
    if not SUMMARIZATION_AVAILABLE:
        print("❌ Summarization dependencies not available")
        print("Install with: pip install transformers torch")
        return
    
    vault_path = input("Enter path to your Obsidian vault: ").strip()
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Invalid vault path")
        return
    
    print("\nAvailable models:")
    for key, model_info in ObsidianAISummarizer.MODELS.items():
        recommended = " (RECOMMENDED)" if model_info['recommended'] else ""
        print(f"  {key}: {model_info['description']}{recommended}")
    
    model_choice = input("\nChoose model [distilbart]: ").strip() or 'distilbart'
    
    summarizer = ObsidianAISummarizer(vault_path, model_choice)
    
    def progress_print(msg):
        print(f"   {msg}")
    
    while True:
        print("\nOptions:")
        print("1. 📄 Summarize a file")
        print("2. 📝 Summarize custom text")
        print("3. 📊 View cache statistics")
        print("4. 🗑️  Clear cache")
        print("5. 🚪 Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            file_path = input("Enter relative file path: ").strip()
            if file_path:
                print(f"\n🤖 Summarizing file: {file_path}")
                print("-" * 40)
                result = summarizer.summarize_file(file_path, progress_callback=progress_print)
                
                if 'error' in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"✅ Summary{'(cached)' if result.get('cached') else ''}:")
                    print(f"\n{result['summary']}")
                    if 'metadata' in result:
                        meta = result['metadata']
                        print(f"\nℹ️  Compression: {meta.get('compression_ratio', 0):.1%}")
                        print(f"   Original: {meta.get('original_length', 0)} chars")
                        print(f"   Summary: {meta.get('summary_length', 0)} chars")
        
        elif choice == "2":
            print("Enter text to summarize (end with empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            
            text = '\n'.join(lines)
            if text.strip():
                print(f"\n🤖 Summarizing text...")
                print("-" * 40)
                result = summarizer.summarize_text(text, progress_callback=progress_print)
                
                if 'error' in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"✅ Summary:")
                    print(f"\n{result['summary']}")
        
        elif choice == "3":
            stats = summarizer.get_summary_stats()
            print(f"\n📊 Cache Statistics:")
            print(f"   Total summaries: {stats.get('total_summaries', 0)}")
            print(f"   Cache size: {stats.get('cache_size', '0 MB')}")
            if 'summary_types' in stats:
                print(f"   Summary types: {stats['summary_types']}")
        
        elif choice == "4":
            if summarizer.clear_cache():
                print("✅ Cache cleared")
            else:
                print("❌ Error clearing cache")
        
        elif choice == "5":
            break
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    demo_summarizer()