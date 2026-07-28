from sentence_transformers import SentenceTransformer
from config.logger import logger

try:
    logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("SentenceTransformer model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to initialize SentenceTransformer model: {e}")
    raise

def create_embeddings(texts):
    if not texts:
        return []

    logger.info(f"Generating embeddings for {len(texts)} chunks of text...")
    try:
        embeddings = model.encode(
            texts,
            batch_size=16,
            show_progress_bar=True,
        )
        logger.info("Successfully generated embeddings.")
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise Exception(f"Embedding generation failed: {str(e)}")