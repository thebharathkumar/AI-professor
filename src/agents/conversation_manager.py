"""
Conversation manager for handling multi-turn dialogues with memory
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manage conversation state and history"""

    def __init__(self, student_id: Optional[str] = None, course: str = "ai_ethics"):
        """
        Initialize conversation manager

        Args:
            student_id: Optional identifier for the student
            course: Course context (ai_ethics or business_ethics)
        """
        self.student_id = student_id or f"student_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.course = course
        self.conversation_history: List[Dict[str, str]] = []
        self.metadata = {
            "student_id": self.student_id,
            "course": course,
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history

        Args:
            role: Either 'user' or 'assistant'
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.metadata["last_updated"] = datetime.now().isoformat()

    def get_history(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history

        Args:
            max_messages: Optional limit on number of messages to return

        Returns:
            List of message dictionaries
        """
        if max_messages:
            return self.conversation_history[-max_messages:]
        return self.conversation_history

    def get_api_format_history(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for API calls (without timestamps)

        Args:
            max_messages: Optional limit on number of messages

        Returns:
            List of messages in API format
        """
        history = self.get_history(max_messages)
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]

    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
        self.metadata["cleared_at"] = datetime.now().isoformat()
        logger.info(f"Cleared conversation history for {self.student_id}")

    def save_to_file(self, directory: Path) -> None:
        """
        Save conversation to a JSON file

        Args:
            directory: Directory to save the conversation
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            filename = f"conversation_{self.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = directory / filename

            conversation_data = {
                "metadata": self.metadata,
                "conversation": self.conversation_history
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved conversation to {filepath}")

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

    @classmethod
    def load_from_file(cls, filepath: Path) -> 'ConversationManager':
        """
        Load conversation from a JSON file

        Args:
            filepath: Path to the conversation file

        Returns:
            ConversationManager instance
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            manager = cls(
                student_id=data['metadata']['student_id'],
                course=data['metadata']['course']
            )
            manager.conversation_history = data['conversation']
            manager.metadata = data['metadata']

            logger.info(f"Loaded conversation from {filepath}")
            return manager

        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            raise

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "student_id": self.student_id,
            "course": self.course,
            "message_count": len(self.conversation_history),
            "started_at": self.metadata.get("started_at"),
            "last_updated": self.metadata.get("last_updated")
        }
