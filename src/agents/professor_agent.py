"""
Main agent implementation for Professor Brusseau digital twin
"""
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings
from src.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)


class ProfessorAgent:
    """
    Digital twin agent for Professor James Brusseau

    This agent mimics Professor Brusseau's teaching style, vocabulary,
    and approach to AI Ethics and Business Ethics.
    """

    # Core personality and style prompt for Professor Brusseau
    SYSTEM_PROMPT = """You are Professor James Brusseau, a university professor specializing in AI Ethics and Business Ethics.

Your teaching philosophy and style:
- You believe in making complex ethical concepts accessible and engaging to students
- You use real-world examples and case studies to illustrate theoretical concepts
- You encourage critical thinking and challenge students to consider multiple perspectives
- You are approachable, patient, and genuinely interested in helping students understand difficult material
- You connect ethical theories to contemporary issues, especially in technology and business
- You believe ethics is practical, not just theoretical - it should guide real decisions

Your communication style:
- Clear and conversational, avoiding unnecessary jargon
- You ask thought-provoking questions to guide students toward insights
- You acknowledge the complexity of ethical dilemmas rather than offering simplistic answers
- You reference relevant thinkers and frameworks (utilitarianism, deontology, virtue ethics, care ethics, etc.)
- You draw connections between historical ethical thought and modern challenges
- You're enthusiastic about the subject matter and convey its importance

Your approach to student questions:
- Take questions seriously and respond thoughtfully
- If a question is unclear, ask for clarification
- Break down complex topics into understandable components
- Provide concrete examples to illustrate abstract concepts
- Encourage students to think through implications and applications
- When appropriate, reference course materials they should review

Remember: You are here to facilitate learning, not just provide answers. Help students develop their ethical reasoning capabilities."""

    def __init__(
        self,
        course: str = "ai_ethics",
        model: str = None,
        temperature: float = None
    ):
        """
        Initialize the Professor agent

        Args:
            course: Either 'ai_ethics' or 'business_ethics'
            model: Model to use (defaults to settings)
            temperature: Temperature for generation (defaults to settings)
        """
        self.course = course
        self.model = model or settings.primary_model
        self.temperature = temperature or settings.temperature

        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.openai_api_key)

        # Initialize vector store for the specific course
        collection_name = (
            settings.collection_name_ai_ethics if course == "ai_ethics"
            else settings.collection_name_business_ethics
        )
        self.vector_store = VectorStoreManager(collection_name)

        logger.info(f"Initialized Professor Brusseau agent for {course}")

    def generate_response(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response to a student question

        Args:
            question: Student's question
            conversation_history: Previous conversation messages
            use_rag: Whether to use RAG for context retrieval

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Retrieve relevant context if RAG is enabled
            context = ""
            retrieved_docs = []

            if use_rag:
                retrieved_docs = self.vector_store.search(question)
                if retrieved_docs:
                    context = self._format_context(retrieved_docs)

            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current question with context
            user_message = question
            if context:
                user_message = f"""Based on the course materials below, please answer this question:

COURSE MATERIALS:
{context}

STUDENT QUESTION:
{question}

Please provide a thoughtful response that draws on the course materials while maintaining your characteristic teaching style."""

            messages.append({
                "role": "user",
                "content": user_message
            })

            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=settings.max_tokens,
                temperature=self.temperature,
                messages=messages
            )

            # Extract the text response
            response_text = response.choices[0].message.content

            return {
                "response": response_text,
                "context_used": len(retrieved_docs) > 0,
                "sources": [doc['metadata'].get('source', 'unknown') for doc in retrieved_docs],
                "conversation_history": messages[1:] + [{  # Exclude system message from history
                    "role": "assistant",
                    "content": response_text
                }]
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your question right now. Could you try rephrasing it?",
                "error": str(e)
            }

    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string"""
        context_parts = []

        for i, doc in enumerate(retrieved_docs[:settings.top_k_results], 1):
            source = doc['metadata'].get('filename', 'Unknown source')
            text = doc['text']
            context_parts.append(f"[Source {i}: {source}]\n{text}\n")

        return "\n---\n".join(context_parts)

    def ask_clarifying_question(self, unclear_query: str) -> str:
        """
        Generate a clarifying question when the student's query is unclear

        Args:
            unclear_query: The unclear student query

        Returns:
            A clarifying question
        """
        prompt = f"""A student asked: "{unclear_query}"

This question seems unclear or too vague. As Professor Brusseau, ask a helpful clarifying question that will help you understand what the student is really asking about. Be encouraging and supportive."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating clarifying question: {e}")
            return "Could you help me understand your question better? What specific aspect of this topic are you most interested in?"
