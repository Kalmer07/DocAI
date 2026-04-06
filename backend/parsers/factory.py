"""
Document Parsers - Extract text from various file formats
"""
from abc import ABC, abstractmethod
from typing import Union


class BaseParser(ABC):
    """Abstract base class for document parsers"""
    
    @abstractmethod
    def parse(self, content: bytes) -> str:
        """
        Parse file content and extract text.
        
        Args:
            content: Raw file bytes
            
        Returns:
            Extracted text content
        """
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list:
        """List of supported file extensions"""
        pass


def parse_file_content(content: bytes, extension: str) -> str:
    """
    Factory function to parse file based on extension.
    
    Args:
        content: Raw file bytes
        extension: File extension (without dot)
        
    Returns:
        Extracted text
    """
    parser = get_parser(extension)
    return parser.parse(content)


def get_parser(extension: str) -> BaseParser:
    """
    Get appropriate parser for file extension.
    
    Args:
        extension: File extension (without dot)
        
    Returns:
        Parser instance
        
    Raises:
        ValueError: If extension not supported
    """
    extension = extension.lower().strip('.')
    
    parsers = {
        'txt': TextParser(),
        'md': TextParser(),
        'csv': CSVParser(),
        'pdf': PDFParser(),
        'docx': DOCXParser(),
    }
    
    if extension not in parsers:
        # Fallback to text parser
        return TextParser()
    
    return parsers[extension]
