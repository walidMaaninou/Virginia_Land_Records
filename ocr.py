import os
import ast
import pytesseract
from pdf2image import convert_from_path
from openai import OpenAI

def extract_addresses_from_pdf(filepath: str, openai_api_key: str) -> list[str]:
    """
    Applies OCR on a PDF and uses OpenAI to extract the most likely property address.

    :param filepath: Full path to the PDF file
    :param openai_api_key: OpenAI API key to use for the request
    :return: List with one string (the address), or an error message in a list
    """
    client = OpenAI(api_key=openai_api_key)

    try:
        images = convert_from_path(filepath)
        full_text = ""
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            full_text += f"--- Page {i + 1} ---\n{page_text.strip()}\n\n"
    except Exception as e:
        return [f"OCR failed: {e}"]

    if not full_text.strip():
        return ["⚠️ No text detected in PDF."]

    prompt = f"""
From the text below, extract the **single most likely physical mailing address** (property address).
Output only a **Python list containing one string**, with no explanation:

\"\"\"{full_text[:3000]}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        result = response.choices[0].message.content
        addresses = ast.literal_eval(result.strip())
        return addresses
    except Exception as e:
        return [f"OpenAI error: {e}"]
