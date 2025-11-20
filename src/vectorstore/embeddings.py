"""
Embedding generation for text chunks
"""
import logging
from typing import List
import openai
from config import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using OpenAI or local models"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []

            # OpenAI embeddings
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text string

        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
