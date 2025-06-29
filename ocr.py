import io
import ast
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from openai import OpenAI

def extract_addresses_from_pdf(pdf_bytes: bytes, openai_api_key: str) -> list[str]:
    client = OpenAI(api_key=openai_api_key)

    try:
        full_text = ""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in range(len(doc)):
            pix = doc[page_index].get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            page_text = pytesseract.image_to_string(image)
            full_text += f"--- Page {page_index + 1} ---\n{page_text.strip()}\n\n"
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
        return ast.literal_eval(result.strip())
    except Exception as e:
        return [f"OpenAI error: {e}"]
