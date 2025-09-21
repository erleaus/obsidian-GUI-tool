#!/usr/bin/env python3
"""
Obsidian Conversational AI - RAG Pipeline
Combines semantic search with OpenAI for natural language note queries
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from obsidian_ai_search import ObsidianAISearch
from openai_client import OpenAIClient, OpenAIClientError


class ObsidianConversation:
    """Conversational interface for Obsidian vault analysis using RAG"""
    
    def __init__(self, vault_path: str, config_path: str = None):
        self.vault_path = vault_path
        
        # Initialize semantic search
        self.ai_search = ObsidianAISearch(vault_path)
        
        # Initialize OpenAI client
        try:
            self.openai_client = OpenAIClient(config_path)
        except OpenAIClientError as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            self.openai_client = None
        
        # Configuration
        self.max_context_chunks = int(os.getenv("MAX_CONTEXT_CHUNKS", "10"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
        
        # Setup system prompt
        self._setup_system_prompt()
    
    def is_available(self) -> bool:
        """Check if both AI search and OpenAI are available"""
        return (self.ai_search.is_available() and 
                self.openai_client is not None)
    
    def _setup_system_prompt(self):
        """Setup the system prompt for the assistant"""
        if not self.openai_client:
            return
            
        vault_name = Path(self.vault_path).name
        system_prompt = f"""You are an intelligent assistant specialized in analyzing and answering questions about an Obsidian knowledge vault called "{vault_name}".

Your capabilities:
- You can search through the user's notes semantically to find relevant information
- You understand the content, themes, and relationships between notes
- You can summarize, analyze, and answer questions about the vault content
- You provide accurate, helpful responses based on the actual note content

Guidelines:
- Always base your answers on the provided note content when possible
- If you don't find relevant information in the notes, clearly state that
- Cite specific notes when referencing information (use the file names provided)
- Be conversational but accurate
- If asked to summarize topics you can't find notes about, say so explicitly
- When multiple notes are relevant, synthesize the information thoughtfully

The user can ask you questions like:
- "Summarize all notes I have on climate change"
- "What are my thoughts on productivity?" 
- "Show me notes about machine learning"
- "What connections exist between my psychology and philosophy notes?"

Always provide helpful, accurate responses based on the actual vault content."""

        self.openai_client.add_system_message(system_prompt)
    
    def initialize_search_index(self) -> bool:
        """Initialize the semantic search index"""
        if not self.ai_search.is_available():
            print("❌ AI search not available. Please install dependencies.")
            return False
        
        print("🤖 Initializing search index...")
        
        # Try to load existing cache
        if self.ai_search.load_cache():
            print("✅ Search index loaded from cache")
            return True
        
        # Build new index
        print("🔨 Building new search index...")
        if self.ai_search.build_index():
            print("✅ Search index built successfully")
            return True
        else:
            print("❌ Failed to build search index")
            return False
    
    def search_vault_content(self, query: str, max_chunks: int = None) -> List[Dict]:
        """Search vault content for relevant information"""
        if not self.ai_search.is_available():
            return []
        
        max_chunks = max_chunks or self.max_context_chunks
        
        # Perform semantic search
        results = self.ai_search.semantic_search(
            query, 
            top_k=max_chunks * 2,  # Get more results to filter
            min_similarity=self.similarity_threshold
        )
        
        # Group by file to avoid too many chunks from same file
        file_chunks = {}
        for result in results:
            file_path = result['file']
            if file_path not in file_chunks:
                file_chunks[file_path] = []
            file_chunks[file_path].append(result)
        
        # Take best chunks while maintaining diversity
        selected_chunks = []
        files_used = set()
        
        # First pass: take best chunk from each file
        for file_path, chunks in file_chunks.items():
            if len(selected_chunks) < max_chunks:
                best_chunk = max(chunks, key=lambda x: x['similarity'])
                selected_chunks.append(best_chunk)
                files_used.add(file_path)
        
        # Second pass: fill remaining slots with next best chunks
        for file_path, chunks in file_chunks.items():
            remaining_chunks = [c for c in chunks if c not in selected_chunks]
            for chunk in remaining_chunks:
                if len(selected_chunks) < max_chunks:
                    selected_chunks.append(chunk)
                else:
                    break
        
        # Sort by similarity
        selected_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        
        return selected_chunks[:max_chunks]
    
    def build_context_from_search(self, search_results: List[Dict]) -> str:
        """Build context string from search results"""
        if not search_results:
            return "No relevant notes found in the vault."
        
        context_parts = []
        context_parts.append("Here are the most relevant notes from the vault:\n")
        
        for i, result in enumerate(search_results, 1):
            similarity_pct = int(result['similarity'] * 100)
            context_parts.append(f"\n--- Note {i}: {result['file']} (relevance: {similarity_pct}%) ---")
            context_parts.append(result['content'])
            context_parts.append("") # Empty line for readability
        
        return "\n".join(context_parts)
    
    def ask_question(self, question: str, stream: bool = False) -> str:
        """Ask a question about the vault content"""
        if not self.is_available():
            return "❌ Conversational AI not available. Please check your setup."
        
        print(f"🔍 Searching vault for: {question}")
        
        # Search for relevant content
        search_results = self.search_vault_content(question)
        
        if not search_results:
            context = "No relevant notes found in the vault for this query."
            sources = []
        else:
            context = self.build_context_from_search(search_results)
            sources = [result['file'] for result in search_results]
            print(f"📚 Found {len(search_results)} relevant chunks from {len(set(sources))} files")
        
        # Build the user message with context
        user_message = f"""Based on the notes in my vault, please answer this question: {question}

{context}

Please provide a helpful answer based on the note content above. If the notes don't contain relevant information about the question, please say so clearly."""
        
        try:
            if stream:
                print("🤖 Assistant: ", end="", flush=True)
                response_parts = []
                for chunk in self.openai_client.chat_completion(user_message, sources, stream=True):
                    print(chunk, end="", flush=True)
                    response_parts.append(chunk)
                print()  # New line after streaming
                return "".join(response_parts)
            else:
                print("🤖 Generating response...")
                response = self.openai_client.chat_completion(user_message, sources)
                return response
                
        except OpenAIClientError as e:
            return f"❌ Error generating response: {e}"
    
    def get_vault_summary(self) -> str:
        """Get a summary of the entire vault content"""
        print("📊 Analyzing vault content...")
        
        # Get a broad sample of content
        if not self.ai_search.embeddings or not self.ai_search.documents:
            return "❌ No indexed content available. Please build the search index first."
        
        # Sample diverse content from the vault
        total_docs = len(self.ai_search.documents)
        sample_size = min(20, total_docs)
        
        # Take a distributed sample
        step = max(1, total_docs // sample_size)
        sampled_docs = self.ai_search.documents[::step][:sample_size]
        
        # Build context
        context_parts = ["Here's a sample of content from the vault:\n"]
        for i, doc in enumerate(sampled_docs, 1):
            context_parts.append(f"\n--- File {i}: {doc['file']} ---")
            context_parts.append(doc['preview'])  # Use preview for brevity
        
        context = "\n".join(context_parts)
        
        user_message = f"""Please analyze this Obsidian vault and provide a comprehensive summary including:

1. Main themes and topics covered
2. Types of content (notes, ideas, projects, etc.)
3. Overall knowledge areas
4. Any patterns you notice

{context}

Provide a helpful overview of what this vault contains and how it's organized."""
        
        try:
            print("🤖 Generating vault summary...")
            sources = [doc['file'] for doc in sampled_docs]
            response = self.openai_client.chat_completion(user_message, sources)
            return response
        except OpenAIClientError as e:
            return f"❌ Error generating summary: {e}"
    
    def suggest_connections(self, max_suggestions: int = 5) -> str:
        """Suggest potential connections between notes"""
        if not self.ai_search.documents:
            return "❌ No indexed content available."
        
        # Find some potentially related but unlinked notes
        # This is a simplified version - you could make this more sophisticated
        sample_files = []
        seen_files = set()
        
        for doc in self.ai_search.documents:
            if doc['file'] not in seen_files and len(sample_files) < 10:
                sample_files.append(doc)
                seen_files.add(doc['file'])
        
        if len(sample_files) < 2:
            return "❌ Not enough content to suggest connections."
        
        context_parts = ["Here are some notes from the vault:\n"]
        for i, doc in enumerate(sample_files, 1):
            context_parts.append(f"\n--- File {i}: {doc['file']} ---")
            context_parts.append(doc['preview'])
        
        context = "\n".join(context_parts)
        
        user_message = f"""Based on these notes from the vault, please suggest {max_suggestions} potential connections or relationships that could be made between different notes:

{context}

For each suggestion, explain:
1. Which notes could be connected
2. What the relationship or connection would be
3. Why this connection would be valuable

Focus on meaningful intellectual connections rather than superficial similarities."""
        
        try:
            print("🔗 Analyzing potential connections...")
            sources = [doc['file'] for doc in sample_files]
            response = self.openai_client.chat_completion(user_message, sources)
            return response
        except OpenAIClientError as e:
            return f"❌ Error suggesting connections: {e}"
    
    def export_conversation(self, format: str = "markdown") -> str:
        """Export the conversation history"""
        if not self.openai_client:
            return "❌ OpenAI client not available"
        
        return self.openai_client.export_conversation(format)
    
    def clear_conversation(self):
        """Clear the conversation history"""
        if self.openai_client:
            self.openai_client.clear_conversation()
            self._setup_system_prompt()  # Re-add system prompt
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.openai_client:
            return {"error": "OpenAI client not available"}
        
        history = self.openai_client.conversation_history
        
        total_messages = len(history)
        user_messages = len([msg for msg in history if msg.role == "user"])
        assistant_messages = len([msg for msg in history if msg.role == "assistant"])
        total_tokens = self.openai_client.get_conversation_tokens()
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_tokens": total_tokens,
            "model": self.openai_client.model
        }


def demo_conversation():
    """Demo function for the conversational interface"""
    print("🤖 Obsidian Conversational AI Demo")
    print("=" * 50)
    
    # Get vault path
    vault_path = input("Enter path to your Obsidian vault: ").strip()
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Invalid vault path")
        return
    
    # Initialize conversation
    conversation = ObsidianConversation(vault_path)
    
    if not conversation.is_available():
        print("❌ Conversational AI not available. Please check your setup.")
        return
    
    # Initialize search index
    if not conversation.initialize_search_index():
        return
    
    print("\n🎉 Conversational AI Ready!")
    print("\nExample queries:")
    print("- 'Summarize all notes I have on productivity'")
    print("- 'What are my thoughts on machine learning?'")
    print("- 'Show me notes about psychology'")
    print("- 'Get a summary of my entire vault'")
    print("- 'Suggest connections between my notes'")
    print("\nType 'quit' to exit, 'clear' to clear conversation, 'stats' for statistics")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💭 Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.lower() == 'clear':
                conversation.clear_conversation()
                print("✅ Conversation cleared")
                continue
            
            if user_input.lower() == 'stats':
                stats = conversation.get_conversation_stats()
                print(f"\n📊 Conversation Stats:")
                print(f"   Messages: {stats.get('total_messages', 0)}")
                print(f"   Tokens used: {stats.get('total_tokens', 0)}")
                print(f"   Model: {stats.get('model', 'Unknown')}")
                continue
            
            if user_input.lower() in ['vault summary', 'summary']:
                response = conversation.get_vault_summary()
            elif user_input.lower() in ['connections', 'suggest connections']:
                response = conversation.suggest_connections()
            else:
                response = conversation.ask_question(user_input, stream=True)
            
            if not user_input.lower() in ['vault summary', 'summary', 'connections', 'suggest connections']:
                continue  # Response already streamed
            
            print(f"\n🤖 Assistant:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    demo_conversation()