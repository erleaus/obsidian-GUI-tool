#!/usr/bin/env python3
"""
OpenAI Client Wrapper with Error Handling and Rate Limiting
Provides a robust interface to OpenAI API with conversation capabilities
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

try:
    import openai
    from openai import OpenAI
    import tiktoken
    from dotenv import load_dotenv
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI dependencies not installed. Run:")
    print("   pip install openai python-dotenv tiktoken")


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    tokens: int = 0
    sources: List[str] = None


@dataclass 
class RateLimitInfo:
    """Tracks rate limiting information"""
    requests_made: int = 0
    reset_time: datetime = None
    delay_seconds: float = 1.0


class OpenAIClientError(Exception):
    """Custom exception for OpenAI client errors"""
    def __init__(self, message: str, error_type: str = "general", retry_after: int = None):
        super().__init__(message)
        self.error_type = error_type
        self.retry_after = retry_after


class OpenAIClient:
    """Enhanced OpenAI client with conversation management and error handling"""
    
    def __init__(self, config_path: str = None):
        # Load environment variables
        if config_path and os.path.exists(config_path):
            load_dotenv(config_path)
        else:
            load_dotenv()  # Load from .env file if it exists
            
        if not OPENAI_AVAILABLE:
            raise OpenAIClientError("OpenAI dependencies not available", "dependency_error")
            
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise OpenAIClientError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable.",
                "authentication_error"
            )
            
        self.client = OpenAI(api_key=api_key)
        
        # Configuration
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
        
        # Rate limiting
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))
        self.rate_limit = RateLimitInfo()
        
        # Token management
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback for newer models
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
        # Conversation management
        self.conversation_history: List[ConversationMessage] = []
        self.max_context_length = self._get_model_context_length()
        
        # Logging
        logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def _get_model_context_length(self) -> int:
        """Get the maximum context length for the current model"""
        context_lengths = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
        }
        
        # Check for exact match or partial match
        for model_name, length in context_lengths.items():
            if self.model.startswith(model_name):
                return length
                
        # Default fallback
        return 4096
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Token counting failed: {e}")
            # Fallback: rough estimation (4 chars per token)
            return len(text) // 4
    
    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of messages"""
        total_tokens = 0
        for message in messages:
            # Add tokens for the message content
            total_tokens += self.count_tokens(message.get("content", ""))
            # Add overhead tokens for message formatting
            total_tokens += 4  # Approximate overhead per message
        
        total_tokens += 2  # Overhead for the conversation
        return total_tokens
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        
        # Reset counter if a minute has passed
        if self.rate_limit.reset_time and now > self.rate_limit.reset_time:
            self.rate_limit.requests_made = 0
            self.rate_limit.reset_time = None
        
        # Check if we're over the limit
        if self.rate_limit.requests_made >= self.max_requests_per_minute:
            if not self.rate_limit.reset_time:
                self.rate_limit.reset_time = now + timedelta(minutes=1)
            
            sleep_time = (self.rate_limit.reset_time - now).total_seconds()
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.1f} seconds.")
                time.sleep(sleep_time)
                self.rate_limit.requests_made = 0
                self.rate_limit.reset_time = None
    
    def _handle_api_error(self, error: Exception, attempt: int) -> bool:
        """Handle API errors and determine if retry should be attempted"""
        if isinstance(error, openai.RateLimitError):
            retry_after = getattr(error, 'retry_after', None) or self.retry_delay * (2 ** attempt)
            self.logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds.")
            time.sleep(retry_after)
            return True
            
        elif isinstance(error, openai.APIConnectionError):
            self.logger.warning(f"API connection error: {error}")
            if attempt < self.retry_attempts:
                time.sleep(self.retry_delay * (2 ** attempt))
                return True
                
        elif isinstance(error, openai.APITimeoutError):
            self.logger.warning(f"API timeout error: {error}")
            if attempt < self.retry_attempts:
                time.sleep(self.retry_delay * (2 ** attempt))
                return True
                
        elif isinstance(error, openai.AuthenticationError):
            raise OpenAIClientError(
                "Authentication failed. Please check your OpenAI API key.",
                "authentication_error"
            )
            
        elif isinstance(error, openai.PermissionDeniedError):
            raise OpenAIClientError(
                "Permission denied. Your API key may not have access to this model.",
                "permission_error"
            )
            
        return False
    
    def add_system_message(self, content: str):
        """Add a system message to the conversation"""
        message = ConversationMessage(
            role="system",
            content=content,
            timestamp=datetime.now(),
            tokens=self.count_tokens(content)
        )
        self.conversation_history.insert(0, message)  # System messages go at the beginning
    
    def add_user_message(self, content: str, sources: List[str] = None):
        """Add a user message to the conversation"""
        message = ConversationMessage(
            role="user",
            content=content,
            timestamp=datetime.now(),
            tokens=self.count_tokens(content),
            sources=sources or []
        )
        self.conversation_history.append(message)
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation"""
        message = ConversationMessage(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            tokens=self.count_tokens(content)
        )
        self.conversation_history.append(message)
    
    def get_conversation_tokens(self) -> int:
        """Get total tokens in the current conversation"""
        return sum(msg.tokens for msg in self.conversation_history)
    
    def trim_conversation(self, max_tokens: int = None):
        """Trim conversation to fit within token limits"""
        if max_tokens is None:
            max_tokens = self.max_context_length - self.max_tokens - 500  # Reserve space
        
        current_tokens = self.get_conversation_tokens()
        
        if current_tokens <= max_tokens:
            return
        
        # Keep system messages and trim from the oldest user/assistant messages
        system_messages = [msg for msg in self.conversation_history if msg.role == "system"]
        other_messages = [msg for msg in self.conversation_history if msg.role != "system"]
        
        # Calculate tokens for system messages
        system_tokens = sum(msg.tokens for msg in system_messages)
        available_tokens = max_tokens - system_tokens
        
        # Keep most recent messages that fit
        trimmed_messages = []
        current_tokens = 0
        
        for message in reversed(other_messages):
            if current_tokens + message.tokens <= available_tokens:
                trimmed_messages.insert(0, message)
                current_tokens += message.tokens
            else:
                break
        
        self.conversation_history = system_messages + trimmed_messages
        self.logger.info(f"Conversation trimmed to {len(self.conversation_history)} messages")
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Convert conversation history to OpenAI API format"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.conversation_history
        ]
    
    def chat_completion(self, user_message: str = None, sources: List[str] = None, 
                       stream: bool = False) -> str:
        """Send a chat completion request"""
        if user_message:
            self.add_user_message(user_message, sources)
        
        # Trim conversation if needed
        self.trim_conversation()
        
        messages = self.get_messages_for_api()
        
        for attempt in range(self.retry_attempts + 1):
            try:
                self._check_rate_limit()
                self.rate_limit.requests_made += 1
                
                if stream:
                    return self._stream_completion(messages)
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                    
                    assistant_message = response.choices[0].message.content
                    self.add_assistant_message(assistant_message)
                    
                    return assistant_message
                    
            except Exception as error:
                if attempt == self.retry_attempts or not self._handle_api_error(error, attempt):
                    raise OpenAIClientError(f"API request failed: {str(error)}")
    
    def _stream_completion(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream a chat completion response"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Add the complete response to conversation history
            self.add_assistant_message(full_response)
            
        except Exception as error:
            raise OpenAIClientError(f"Streaming failed: {str(error)}")
    
    def export_conversation(self, format: str = "json") -> str:
        """Export conversation history"""
        if format.lower() == "json":
            return json.dumps([
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "tokens": msg.tokens,
                    "sources": msg.sources
                }
                for msg in self.conversation_history
            ], indent=2)
        
        elif format.lower() == "markdown":
            md_content = "# Conversation History\n\n"
            for msg in self.conversation_history:
                if msg.role == "system":
                    continue  # Skip system messages in markdown export
                    
                role_name = "**You**" if msg.role == "user" else "**Assistant**"
                md_content += f"{role_name} ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}):\n\n"
                md_content += f"{msg.content}\n\n"
                
                if msg.sources:
                    md_content += "*Sources:*\n"
                    for source in msg.sources:
                        md_content += f"- {source}\n"
                    md_content += "\n"
                
                md_content += "---\n\n"
            
            return md_content
        
        else:
            raise ValueError("Format must be 'json' or 'markdown'")


def test_openai_client():
    """Test function for the OpenAI client"""
    try:
        client = OpenAIClient()
        print("✅ OpenAI client initialized successfully")
        
        # Test basic completion
        client.add_system_message("You are a helpful assistant for analyzing Obsidian notes.")
        response = client.chat_completion("Hello! Can you help me analyze my notes?")
        
        print(f"🤖 Response: {response}")
        print(f"📊 Total tokens used: {client.get_conversation_tokens()}")
        
        return True
        
    except OpenAIClientError as e:
        print(f"❌ OpenAI client error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_openai_client()