from ocr import extract_addresses_from_pdf

pdf_path = "downloads/3045359.pdf"
addresses = extract_addresses_from_pdf(pdf_path)

print("Extracted Address:", addresses[0] if addresses else "None")
