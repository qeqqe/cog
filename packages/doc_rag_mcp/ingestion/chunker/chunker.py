import nltk
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

MODEL_NAME = "BAAI/bge-m3"
model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
encode_kwargs = {'normalize_embeddings': True}

embeddings_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

def semantic_chunker(text: str, threshold: float = 0.95, max_tokens: int = 1024) -> list[str]:
    """Semantic chunker splits text into meaningful chunks based on semantic similarity.
    Args:
        text: input text.
        threshold: similarity threshold for chunking.
        max_tokens: max number of tokens per chunk.
    """
    sentences = nltk.sent_tokenize(text)
    
    if len(sentences) < 2:
        return sentences

    embeddings = embeddings_model.embed_documents(sentences)
    
    similarities = []
    for i in range(len(embeddings) - 1):
        emb1 = np.array(embeddings[i]).reshape(1, -1)
        emb2 = np.array(embeddings[i+1]).reshape(1, -1)
        sim = cosine_similarity(emb1, emb2)[0][0]
        similarities.append(sim)

    chunks = []
    current_chunk_sentences = [sentences[0]]
    current_token_count = len(sentences[0].split())
    
    for i in range(len(similarities)):
        next_sentence = sentences[i+1]
        next_tokens = len(next_sentence.split())
        
        should_break = (similarities[i] < threshold or 
                       current_token_count + next_tokens > max_tokens)
        
        if should_break and current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [next_sentence]
            current_token_count = next_tokens
        else:
            current_chunk_sentences.append(next_sentence)
            current_token_count += next_tokens
            
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
    
    return chunks

def chunk_content(text: str, max_tokens: int = 1024, threshold: float = 0.95) -> list[str]:
    if not text or not isinstance(text, str):
        logger.warning("Got empty or invalid text")
        return []
    
    try:
        chunks = semantic_chunker(text, threshold=threshold, max_tokens=max_tokens)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error during chunking: {e}")
        return [text]