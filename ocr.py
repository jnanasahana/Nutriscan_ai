import pytesseract
from PIL import Image

def image_to_text(image_path: str) -> str:
    """Extract text from an image using Tesseract OCR"""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"OCR Error: {str(e)}"
