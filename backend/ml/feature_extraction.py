import re
import string

FINANCIAL_STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
    'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
    'it', 'its', 'this', 'that', 'these', 'those', 'which', 'who', 'whom', 'what'
}

def clean_financial_text(text: str) -> str:
    """
    Cleans financial text while preserving tickers, percentages, and financial signifiers.
    """
    if not text:
        return ""
    
    # Preserve ticker casing by tokenizing, normalize other text
    text = text.strip()
    
    # Replace URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Keep alphanumeric, $, %, +, -, and spaces
    text = re.sub(r'[^\w\s\$\%\+\-\.]', ' ', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_financial(text: str) -> list[str]:
    """
    Tokenizes text into words and tickers.
    """
    cleaned = clean_financial_text(text)
    tokens = cleaned.split()
    return [t for t in tokens if t.lower() not in FINANCIAL_STOPWORDS and len(t) > 1]
