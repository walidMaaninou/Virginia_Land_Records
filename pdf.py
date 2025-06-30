import requests
import os
PDF_URL = "https://risweb.vacourts.gov/jsra/sra/api/search/getPdfImage"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0"
}

def download_pdf_to_file(token: str, urowid: str, instr_group: str, fips: str, verified: str = "VER", save_dir="downloads") -> str:
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

    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"{urowid}.pdf")
    with open(filepath, "wb") as f:
        f.write(response.content)
    return filepath
