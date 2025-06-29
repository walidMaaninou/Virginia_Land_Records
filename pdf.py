import requests

PDF_URL = "https://risweb.vacourts.gov/jsra/sra/api/search/getPdfImage"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0"
}


def download_pdf(token: str, urowid: str, instr_group: str, fips: str, verified: str = "VER", output_dir="downloads"):
    """
    Downloads the PDF associated with the urowid and saves it locally.

    :param token: Bearer token from login
    :param urowid: Unique record ID
    :param instr_group: Group (usually "LR")
    :param fips: FIPS code (usually "710")
    :param verified: "VER" by default
    :param output_dir: Directory to save files
    :return: File path of the downloaded PDF
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

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

    file_path = os.path.join(output_dir, f"{urowid}.pdf")
    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path
