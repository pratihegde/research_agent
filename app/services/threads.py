"""
Thread management service for conversation persistence
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime


class Message:
    """Represents a single message in a conversation"""
    def __init__(self, role: str, content: str, timestamp: Optional[str] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"


class ConversationThread:
    """Represents a conversation thread with message history"""
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.messages: List[Message] = []
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
    
    def add_message(self, role: str, content: str):
        """Add a message to the thread"""
        message = Message(role, content)
        self.messages.append(message)
        self.updated_at = datetime.utcnow().isoformat() + "Z"
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get message history as list of dicts"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.messages
        ]


class ThreadManager:
    """
    Manages conversation threads in memory.
    
    In production, this would be replaced with a database-backed solution.
    """
    
    def __init__(self):
        self.threads: Dict[str, ConversationThread] = {}
    
    def create_thread(self) -> str:
        """Create a new conversation thread and return its ID"""
        thread_id = str(uuid.uuid4())
        self.threads[thread_id] = ConversationThread(thread_id)
        return thread_id
    
    def get_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get an existing thread by ID"""
        return self.threads.get(thread_id)
    
    def get_or_create_thread(self, thread_id: Optional[str] = None) -> tuple[str, ConversationThread]:
        """
        Get existing thread or create new one.
        
        Args:
            thread_id: Optional thread ID to retrieve
            
        Returns:
            Tuple of (thread_id, thread)
        """
        if thread_id and thread_id in self.threads:
            return thread_id, self.threads[thread_id]
        
        # Create new thread
        new_id = self.create_thread()
        return new_id, self.threads[new_id]
    
    def add_message(self, thread_id: str, role: str, content: str):
        """Add a message to a thread"""
        thread = self.get_thread(thread_id)
        if thread:
            thread.add_message(role, content)
    
    def get_thread_count(self) -> int:
        """Get total number of threads"""
        return len(self.threads)


# Singleton instance
_thread_manager = None

def get_thread_manager() -> ThreadManager:
    """Get or create the singleton thread manager instance"""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager
