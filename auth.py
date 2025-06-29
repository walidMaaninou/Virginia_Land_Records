import requests
import time

LOGIN_URL = "https://risweb.vacourts.gov/jsra/sra/srauser/login"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "Basic c3JhYWRtaW46c3JhYWRtaW4=",  # base64("sraadmin:sraadmin")
    "Cache-control": "no-store",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://risweb.vacourts.gov",
    "Referer": "https://risweb.vacourts.gov/jsra/sra/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "DNT": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

def get_access_token(username: str, password: str, retries: int = 1, delay: float = 1.5) -> str:
    """
    Logs into the Virginia Court system and returns the access token.
    Automatically retries once on 'UserAlreadyLoggedInException'.
    """
    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    for attempt in range(retries + 1):
        response = requests.post(LOGIN_URL, headers=HEADERS, data=data)

        if response.ok:
            return response.json().get("access_token")

        # If duplicate session error, retry
        if response.status_code == 400 and "UserAlreadyLoggedInException" in response.text:
            if attempt < retries:
                time.sleep(delay)
                continue

        raise Exception(f"Login failed: {response.status_code} - {response.text}")
