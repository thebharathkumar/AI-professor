"""
Video processor for extracting transcripts from video lectures
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("youtube-transcript-api not available")


class VideoProcessor:
    """Process video files and extract transcripts"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def get_youtube_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Extract transcript from YouTube video

        Args:
            video_id: YouTube video ID

        Returns:
            List of text chunks with metadata
        """
        if not YOUTUBE_AVAILABLE:
            logger.error("YouTube transcript API not available")
            return []

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine transcript segments into full text
            full_text = " ".join([entry['text'] for entry in transcript])

            # Create chunks
            chunks = []
            text_chunks = self._create_chunks(full_text)

            for idx, chunk in enumerate(text_chunks):
                chunks.append({
                    "text": chunk,
                    "source": f"https://youtube.com/watch?v={video_id}",
                    "source_type": "youtube_video",
                    "chunk_id": idx,
                    "metadata": {
                        "video_id": video_id,
                        "duration": transcript[-1]['start'] + transcript[-1]['duration'] if transcript else 0
                    }
                })

            logger.info(f"Processed YouTube video {video_id}: {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing YouTube video {video_id}: {e}")
            return []

    def process_transcript_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a pre-downloaded transcript file (JSON or TXT format)

        Args:
            file_path: Path to transcript file

        Returns:
            List of text chunks with metadata
        """
        try:
            if file_path.suffix.lower() == '.json':
                return self._process_json_transcript(file_path)
            else:
                return self._process_text_transcript(file_path)

        except Exception as e:
            logger.error(f"Error processing transcript file {file_path}: {e}")
            return []

    def _process_json_transcript(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process JSON format transcript"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON formats
        if isinstance(data, list):
            # Format: [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
            full_text = " ".join([entry.get('text', '') for entry in data])
        elif isinstance(data, dict) and 'text' in data:
            # Format: {"text": "full transcript", ...}
            full_text = data['text']
        else:
            logger.warning(f"Unknown JSON format in {file_path}")
            return []

        chunks = []
        text_chunks = self._create_chunks(full_text)

        for idx, chunk in enumerate(text_chunks):
            chunks.append({
                "text": chunk,
                "source": str(file_path),
                "source_type": "transcript_json",
                "chunk_id": idx,
                "metadata": {
                    "filename": file_path.name
                }
            })

        logger.info(f"Processed JSON transcript {file_path.name}: {len(chunks)} chunks")
        return chunks

    def _process_text_transcript(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process plain text transcript"""
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        chunks = []
        text_chunks = self._create_chunks(full_text)

        for idx, chunk in enumerate(text_chunks):
            chunks.append({
                "text": chunk,
                "source": str(file_path),
                "source_type": "transcript_txt",
                "chunk_id": idx,
                "metadata": {
                    "filename": file_path.name
                }
            })

        logger.info(f"Processed text transcript {file_path.name}: {len(chunks)} chunks")
        return chunks

    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text or len(text.strip()) == 0:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < text_length:
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks
