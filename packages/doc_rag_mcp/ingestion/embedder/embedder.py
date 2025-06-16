from langchain_huggingface import HuggingFaceEmbeddings
import torch

def embed_text(text: str) -> list:
    """Embed.

    Args:
        text: The text to embed.
    Returns:
        list: The embedded float of the text.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty or None")
    
    try:
        model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        encode_kwargs = {'normalize_embeddings': True} 

        embeddings_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
        embedding = embeddings_model.embed_query(text.strip())
        if not embedding:
                raise RuntimeError("Empty result")
        return embedding
    except Exception as e:
        raise RuntimeError(f"Failed to embed text: {str(e)}") from e
    
    
    
    
if __name__ == "__main__":
    # Example usage
    text = "This is a sample text to be embedded."
    try:
        embedding = embed_text(text)
        print("Embedding successful:", len(embedding))
    except Exception as e:
        print("Error embedding text:", str(e))