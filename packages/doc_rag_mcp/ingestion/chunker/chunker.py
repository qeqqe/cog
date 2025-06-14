from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama.embeddings import OllamaEmbeddings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="bge-m3",
)

def chunk_content(content: str) -> list:
    if not content or not isinstance(content, str):
        logger.error("Content can't be empty & should be a string.")
        raise ValueError("Content can't be empty & should be a string.")

    try:
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            buffer_size=3,  
            breakpoint_threshold_type="standard_deviation",
            breakpoint_threshold_amount=0.8, 
            sentence_split_regex=r"(?<=[.?!])\\s+",
            min_chunk_size=250, 
            add_start_index=True,
        )
        docs = text_splitter.create_documents([content])
        if not docs:
            logger.warning(f"nothing was created from the provided content. Content length: {len(content)}")
            return []
            
        for doc_index, doc in enumerate(docs):
            logger.info(f"Chunk {doc_index + 1} created with {len(doc.page_content)} characters.")
        return docs
    
    except ValueError as ve:  
        logger.error(f"ValueError during chunking: {ve}")
        raise  
    except Exception as e:
        logger.error(f"An unexpected error occurred while chunking the content: {e}", exc_info=True)
        raise Exception(f"An error occurred while chunking the content: {e}")