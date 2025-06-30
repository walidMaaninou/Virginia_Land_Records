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


def search_names(token: str, search_term: str = "aa", instr_types=None, from_date="04/01/2025", to_date="06/29/2025", max_pages: int = 100):
    """
    Generator that yields pages of names from the Virginia Court search API.

    :param token: Bearer access token from login
    :param search_term: Initial search input
    :param instr_types: List of selected instrument type codes
    :param from_date: Search window start date (MM/DD/YYYY)
    :param to_date: Search window end date (MM/DD/YYYY)
    :param max_pages: Safety limit for max number of pages
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
            "srchFromDt": from_date,
            "srchToDt": to_date,
            "instr_type": instr_types or BASE_PAYLOAD["instr_type"],
        })

        response = requests.post(SEARCH_URL, headers=headers, json=payload)
        if not response.ok:
            raise Exception(f"Search request failed: {response.status_code} - {response.text}")

        results = response.json()
        if not results:
            break

        last_name = results[-1]['name']
        if last_name in seen:
            break
        seen.add(last_name)

        yield results
        reference_name = last_name

