"""
Concrete Parser Implementations
"""
from parsers.factory import BaseParser


class TextParser(BaseParser):
    """Parser for plain text files"""
    
    def parse(self, content: bytes) -> str:
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1')
    
    @property
    def supported_extensions(self) -> list:
        return ['txt', 'md', 'log']


class CSVParser(BaseParser):
    """Parser for CSV files"""
    
    def parse(self, content: bytes) -> str:
        text = content.decode('utf-8')
        # Keep as-is, AI will interpret structure
        return text
    
    @property
    def supported_extensions(self) -> list:
        return ['csv']


class PDFParser(BaseParser):
    """Parser for PDF files using PyMuPDF"""
    
    def parse(self, content: bytes) -> str:
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            
            for page in doc:
                text_parts.append(page.get_text())
            
            doc.close()
            return "\n\n--- PAGE BREAK ---\n\n".join(text_parts)
            
        except ImportError:
            return "[PDF parsing requires PyMuPDF: pip install pymupdf]"
        except Exception as e:
            return f"[PDF parse error: {str(e)}]"
    
    @property
    def supported_extensions(self) -> list:
        return ['pdf']


class DOCXParser(BaseParser):
    """Parser for DOCX files using python-docx"""
    
    def parse(self, content: bytes) -> str:
        try:
            from docx import Document
            import io
            
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            return "\n\n".join(paragraphs)
            
        except ImportError:
            return "[DOCX parsing requires python-docx: pip install python-docx]"
        except Exception as e:
            return f"[DOCX parse error: {str(e)}]"
    
    @property
    def supported_extensions(self) -> list:
        return ['docx', 'doc']
