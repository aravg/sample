import time
import warnings
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseAgent:
    def fetch_with_retry(self, url: str, max_retries: int = 3, backoff: float = 1.0) -> dict:
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10, verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(backoff * (2 ** attempt))
        raise RuntimeError(f"All {max_retries} attempts failed: {last_error}")
