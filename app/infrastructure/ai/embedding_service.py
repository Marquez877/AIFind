"""Embedding service for generating vector embeddings using OpenAI."""

from openai import AsyncOpenAI

from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI API."""

    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    async def get_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        client = self._get_client()
        
        # Clean and truncate text if necessary
        text = text.replace("\n", " ").strip()
        if not text:
            return [0.0] * self.DIMENSIONS
        
        response = await client.embeddings.create(
            model=self.MODEL,
            input=text,
            dimensions=self.DIMENSIONS,
        )
        
        return response.data[0].embedding

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a single API call."""
        client = self._get_client()
        
        # Clean texts
        cleaned_texts = [t.replace("\n", " ").strip() for t in texts]
        
        # Filter empty texts and track their positions
        non_empty_indices = [i for i, t in enumerate(cleaned_texts) if t]
        non_empty_texts = [cleaned_texts[i] for i in non_empty_indices]
        
        if not non_empty_texts:
            return [[0.0] * self.DIMENSIONS for _ in texts]
        
        response = await client.embeddings.create(
            model=self.MODEL,
            input=non_empty_texts,
            dimensions=self.DIMENSIONS,
        )
        
        # Build result with zero vectors for empty texts
        result: list[list[float]] = [[0.0] * self.DIMENSIONS for _ in texts]
        for idx, embedding_data in zip(non_empty_indices, response.data):
            result[idx] = embedding_data.embedding
        
        return result


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: The text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If not at the end, try to break at a sentence or word boundary
        if end < len(text):
            # Try to find sentence boundary
            for sep in [". ", ".\n", "!\n", "?\n", "! ", "? ", "\n\n"]:
                last_sep = text[start:end].rfind(sep)
                if last_sep > chunk_size // 2:  # Only if it's past halfway
                    end = start + last_sep + len(sep)
                    break
            else:
                # Try word boundary
                last_space = text[start:end].rfind(" ")
                if last_space > chunk_size // 2:
                    end = start + last_space + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position, accounting for overlap
        start = end - overlap if end < len(text) else end
    
    return chunks
