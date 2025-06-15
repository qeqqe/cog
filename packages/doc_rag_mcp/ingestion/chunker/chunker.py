import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# For semantic understanding
nlp = spacy.load("en_core_web_md")

def chunk_content(text, max_tokens=2000, overlap=200):
    """Semantically chunks the content based on sentence boundaries and token count
    
    Args:
        text: The text content to be chunked.
        max_tokens: Max number of tokens per chunk.
        overlap: Number of overlapping tokens between chunks.
    """
    # breaks the text into sentences
    sentences = sent_tokenize(text)

    # get embeddings for each sentence
    sentence_embeddings = [nlp(sentence).vector for sentence in sentences]

    # track token count
    token_counts = [len(sentence.split()) for sentence in sentences]


    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for i, sentence in enumerate(sentences):
        # If adding this sentence would exceed our limit, start a new chunk
        if current_token_count + token_counts[i] > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # For overlap, find the most semantically similar sentences to include
            if overlap > 0 and len(current_chunk) > 0:
                # Get embeddings for current chunk sentences
                current_embs = sentence_embeddings[i-len(current_chunk):i]
                # Find sentences with highest similarity to include in overlap
                similarities = cosine_similarity([sentence_embeddings[i]], current_embs)[0]
                overlap_indices = np.argsort(similarities)[-int(overlap/10):]  # Heuristic for number of sentences
                
                # Add overlapping sentences to new chunk
                current_chunk = [sentences[i-len(current_chunk)+idx] for idx in overlap_indices]
                current_token_count = sum(token_counts[i-len(current_chunk)+idx] for idx in overlap_indices)
            else:
                current_chunk = []
                current_token_count = 0
        
        current_chunk.append(sentence)
        current_token_count += token_counts[i]
    
    # add the last chunk if it's not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks