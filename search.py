import requests

SEARCH_URL = "https://risweb.vacourts.gov/jsra/sra/api/search/getSearchNames"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0"
}

BASE_PAYLOAD = {
    "book_nbr": "",
    "bus_flag": "",
    "exactTaxMapNumFlg": "N",
    "fips": "710",
    "group": ["LR"],
    "instr_nbr": "",
    "instr_type": [
        "AF     ", "DPD    ", "DTD    ", "DD     ", "LM     ", "MEML   ",
        "NOT    ", "NL     ", "NLP    ", "ODRB-PL", "REA    ", "WILL   "
    ],
    "exactSearchNameFlag": "N",
    "name_type": [],
    "navigateFlag": "F",
    "orderByDateFlag": "A",
    "instrPageCnt": 0,
    "srchDescription": "",
    "taxMapNum": "",
    "page_nbr": "",
    "advSearchFlag": False
}


def search_names(token: str, search_term: str = "aa", start_date="4/1/2025", end_date="6/29/2025", max_pages: int = 1):
    """
    Generator that yields pages of names from the Virginia Court search API.

    :param token: Bearer access token from login
    :param search_term: Initial search input
    :param start_date: Start of search window
    :param end_date: End of search window
    :param max_pages: Max number of pages to retrieve
    :yield: List of result dicts per page
    """
    headers = COMMON_HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"

    reference_name = search_term
    seen = set()

    for page in range(max_pages):
        payload = BASE_PAYLOAD.copy()
        payload.update({
            "name": search_term,
            "referenceName": reference_name,
            "srchFromDt": start_date,
            "srchToDt": end_date
        })

        response = requests.post(SEARCH_URL, headers=headers, json=payload)
        if not response.ok:
            raise Exception(f"Search request failed: {response.status_code} - {response.text}")

        results = response.json()
        if not results:
            break

        # Prevent infinite loops if data is repeated
        last_name = results[-1]['name']
        if last_name in seen:
            break
        seen.add(last_name)

        yield results

        reference_name = last_name  # Update referenceName for the next page
