import requests

DETAILS_URL = "https://risweb.vacourts.gov/jsra/sra/api/search/getInstrDetails"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0"
}

BASE_PARAMS = {
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
    "srchFromDt": "4/1/2025",
    "srchToDt": "6/29/2025",
    "taxMapNum": "",
    "page_nbr": "",
    "advSearchFlag": False
}


def get_instr_details(token: str, search_name: str, count: int, business: str, nameflag: str, original_term: str = "aa"):
    """
    Queries getInstrDetails for a specific name result.

    Returns a list of instruction metadata dicts (with urowid, instr_nbr, etc.)
    """
    headers = COMMON_HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"

    payload = {
        "searchFormReqParams": {
            **BASE_PARAMS,
            "name": original_term,
            "referenceName": original_term,
        },
        "searchNamesList": [
            {
                "name": search_name,
                "count": count,
                "business": business,
                "nameflag": nameflag
            }
        ]
    }

    response = requests.post(DETAILS_URL, headers=headers, json=payload)

    if not response.ok:
        raise Exception(f"getInstrDetails failed: {response.status_code} - {response.text}")

    return response.json()  # This is a list of instruction entries (with urowid etc.)
