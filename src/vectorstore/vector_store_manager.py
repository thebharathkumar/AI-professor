"""
Vector store manager for storing and retrieving document embeddings
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from .embeddings import EmbeddingGenerator
from config import settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manage vector store operations for document retrieval"""

    def __init__(self, collection_name: str, persist_directory: str = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.vector_store_path
        self.embedding_generator = EmbeddingGenerator()

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Embeddings for {collection_name}"}
        )

        logger.info(f"Initialized vector store: {collection_name}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store

        Args:
            documents: List of document dicts with 'text', 'source', 'metadata' keys
        """
        if not documents:
            logger.warning("No documents to add")
            return

        try:
            # Extract texts for embedding
            texts = [doc['text'] for doc in documents]

            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} documents...")
            embeddings = self.embedding_generator.generate_embeddings(texts)

            if not embeddings:
                logger.error("Failed to generate embeddings")
                return

            # Prepare data for ChromaDB
            ids = [f"{doc.get('source', 'unknown')}_{doc.get('chunk_id', i)}"
                   for i, doc in enumerate(documents)]

            metadatas = []
            for doc in documents:
                metadata = doc.get('metadata', {}).copy()
                metadata['source'] = doc.get('source', 'unknown')
                metadata['source_type'] = doc.get('source_type', 'unknown')
                metadatas.append(metadata)

            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to vector store")

        except Exception as e:
            logger.error(f"Error adding documents: {e}")

    def search(
        self,
        query: str,
        n_results: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of relevant documents with scores
        """
        try:
            n_results = n_results or settings.top_k_results

            # Generate query embedding
            query_embedding = self.embedding_generator.generate_single_embedding(query)

            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []

            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )

            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def delete_collection(self) -> None:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
