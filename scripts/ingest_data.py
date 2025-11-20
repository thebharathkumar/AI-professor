#!/usr/bin/env python3
"""
Data ingestion script for processing course materials into the vector store
"""
import sys
import logging
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from src.processors import DocumentProcessor, VideoProcessor
from src.vectorstore import VectorStoreManager
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def ingest_documents(
    source_dir: Path,
    course: str,
    file_patterns: List[str] = None
) -> None:
    """
    Ingest documents from a directory into the vector store

    Args:
        source_dir: Directory containing documents
        course: Course name (ai_ethics or business_ethics)
        file_patterns: List of file patterns to process (e.g., ['*.pdf', '*.docx'])
    """
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return

    # Initialize processors
    doc_processor = DocumentProcessor()
    video_processor = VideoProcessor()

    # Get collection name
    collection_name = (
        settings.collection_name_ai_ethics if course == "ai_ethics"
        else settings.collection_name_business_ethics
    )

    # Initialize vector store
    vector_store = VectorStoreManager(collection_name)

    # Collect all documents
    all_chunks = []

    # Default file patterns
    if not file_patterns:
        file_patterns = ['*.pdf', '*.docx', '*.pptx', '*.txt', '*.md']

    # Process each file pattern
    for pattern in file_patterns:
        files = list(source_dir.rglob(pattern))
        logger.info(f"Found {len(files)} files matching {pattern}")

        for file_path in files:
            logger.info(f"Processing {file_path.name}...")
            chunks = doc_processor.process_file(file_path)
            all_chunks.extend(chunks)

    # Process transcript files
    transcript_files = list(source_dir.rglob('*transcript*.json')) + \
                      list(source_dir.rglob('*transcript*.txt'))

    for transcript_file in transcript_files:
        logger.info(f"Processing transcript {transcript_file.name}...")
        chunks = video_processor.process_transcript_file(transcript_file)
        all_chunks.extend(chunks)

    # Add to vector store
    if all_chunks:
        logger.info(f"Adding {len(all_chunks)} chunks to vector store...")
        vector_store.add_documents(all_chunks)
        logger.info("Data ingestion complete!")

        # Print stats
        stats = vector_store.get_collection_stats()
        logger.info(f"Vector store stats: {stats}")
    else:
        logger.warning("No documents were processed")


def ingest_youtube_videos(video_ids: List[str], course: str) -> None:
    """
    Ingest YouTube video transcripts

    Args:
        video_ids: List of YouTube video IDs
        course: Course name
    """
    video_processor = VideoProcessor()

    collection_name = (
        settings.collection_name_ai_ethics if course == "ai_ethics"
        else settings.collection_name_business_ethics
    )

    vector_store = VectorStoreManager(collection_name)

    all_chunks = []
    for video_id in video_ids:
        logger.info(f"Processing YouTube video: {video_id}")
        chunks = video_processor.get_youtube_transcript(video_id)
        all_chunks.extend(chunks)

    if all_chunks:
        logger.info(f"Adding {len(all_chunks)} chunks to vector store...")
        vector_store.add_documents(all_chunks)
        logger.info("YouTube video ingestion complete!")
    else:
        logger.warning("No videos were processed")


def main():
    """Main entry point"""
    setup_logging()

    # Example usage - customize based on your data structure
    logger.info("=== Professor Brusseau Data Ingestion ===")

    # Check if data directories exist
    ai_ethics_dir = settings.raw_data_dir / "ai_ethics"
    business_ethics_dir = settings.raw_data_dir / "business_ethics"

    # Ingest AI Ethics course materials
    if ai_ethics_dir.exists():
        logger.info("\n--- Ingesting AI Ethics Course Materials ---")
        ingest_documents(ai_ethics_dir, "ai_ethics")
    else:
        logger.warning(f"AI Ethics data directory not found: {ai_ethics_dir}")
        logger.info(f"Please create directory and add course materials: {ai_ethics_dir}")

    # Ingest Business Ethics course materials
    if business_ethics_dir.exists():
        logger.info("\n--- Ingesting Business Ethics Course Materials ---")
        ingest_documents(business_ethics_dir, "business_ethics")
    else:
        logger.warning(f"Business Ethics data directory not found: {business_ethics_dir}")
        logger.info(f"Please create directory and add course materials: {business_ethics_dir}")

    # Example: Ingest YouTube videos (uncomment and add actual video IDs)
    # logger.info("\n--- Ingesting YouTube Videos ---")
    # ai_ethics_videos = ["VIDEO_ID_1", "VIDEO_ID_2"]  # Add actual video IDs
    # ingest_youtube_videos(ai_ethics_videos, "ai_ethics")

    logger.info("\n=== Data Ingestion Complete ===")


if __name__ == "__main__":
    main()
