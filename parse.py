import re
import pandas as pd

def parse_product_info(ocr_text):
    """
    Extract product name, brand, nutrition, and ingredients from OCR text.
    """
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    
    # Product name = first non-empty line
    product_name = lines[0] if lines else "Unknown Product"

    # Brand = first line containing 'brand'
    brand = "Unknown Brand"
    for line in lines[:5]:
        if "brand" in line.lower():
            brand = line
            break

    # Detect nutrition info (simplified)
    nutrition = {}
    nutrients = ['calories', 'protein', 'carbohydrates', 'fat', 'sodium']
    for nutrient in nutrients:
        match = re.search(rf'{nutrient}\s*[:\-]?\s*([\d\.]+)', ocr_text, re.I)
        nutrition[nutrient] = float(match.group(1)) if match else 0

    # Extract ingredients (look for line starting with 'ingredients')
    ingredients = []
    for line in lines:
        if 'ingredient' in line.lower():
            line = line.split(':')[-1]  # get content after 'Ingredients:'
            ingredients = [i.strip() for i in line.split(',')]
            break

    # Return as dict
    return {
        'product_name': product_name,
        'brand': brand,
        'nutrition': nutrition,
        'ingredients': ingredients
    }


def parse_ingredients(ocr_text):
    """
    Return a pandas DataFrame of detected ingredients.
    """
    info = parse_product_info(ocr_text)
    return pd.DataFrame({'ingredient': info['ingredients']})


def parse_nutrition(ocr_text):
    """
    Return nutrition as a dictionary.
    """
    info = parse_product_info(ocr_text)
    return info['nutrition']
