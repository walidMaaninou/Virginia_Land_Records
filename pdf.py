import requests

PDF_URL = "https://risweb.vacourts.gov/jsra/sra/api/search/getPdfImage"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0"
}

def download_pdf(token: str, urowid: str, instr_group: str, fips: str, verified: str = "VER") -> bytes:
    """
    Downloads the PDF as bytes for OCR processing.
    
    :param token: Bearer token
    :param urowid: Unique ID of the record
    :param instr_group: Instruction group (e.g., "LR")
    :param fips: County FIPS code (e.g., "710")
    :param verified: Default "VER"
    :return: Raw PDF content in bytes
    """
    headers = COMMON_HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"

    payload = {
        "urowid": urowid,
        "fips": fips,
        "instr_group": instr_group,
        "verified": verified
    }

    response = requests.post(PDF_URL, headers=headers, json=payload)

    if not response.ok or not response.content.startswith(b"%PDF"):
        raise Exception(f"Failed to download PDF for urowid {urowid}: {response.status_code} - {response.text}")

    return response.content
