"""Document processing functionality."""
import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles PDF document loading and processing."""
    
    def __init__(self, chunk_size: int = 7500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def load_pdf(self, file_path: Path) -> List:
        """Load PDF document."""
        try:
            logger.info(f"Loading PDF from {file_path}")
            loader = PyPDFLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def load_multiple_pdfs(self, file_paths: List[Path]) -> List:
        """Load multiple PDF documents and combine them."""
        all_documents = []
        for file_path in file_paths:
            try:
                logger.info(f"Loading PDF from {file_path}")
                docs = self.load_pdf(file_path)
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f"Error loading PDF {file_path}: {e}")
                # Continue with other files even if one fails
                continue
        logger.info(f"Loaded {len(all_documents)} total pages from {len(file_paths)} PDFs")
        return all_documents
    
    def split_documents(self, documents: List) -> List:
        """Split documents into chunks."""
        try:
            logger.info("Splitting documents into chunks")
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise