import requests
from django.conf import settings


class OracleAPIError(Exception):
    pass


def _get_base_url() -> str:
    base = getattr(settings, "ORACLE_BASE_URL", "").rstrip("/")
    if not base:
        raise OracleAPIError("ORACLE_BASE_URL nu este setat în settings.py")
    return base


def fetch_next_direction(oracle_id: str, instruction_number: int) -> dict:
    base = _get_base_url()
    url = f"{base}/direction/{oracle_id}/"

    try:
        resp = requests.get(url, params={"instruction_id": instruction_number}, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise OracleAPIError(f"Eroare request Oracle: {e}")

    try:
        return resp.json()
    except ValueError:
        raise OracleAPIError("Rsp Oracle nu e JSON valid.")


def check_password(code: str) -> dict:
    base = _get_base_url()
    url = f"{base}/check-password/{code}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise OracleAPIError(f"Eroare request Oracle: {e}")

    try:
        return resp.json()
    except ValueError:
        return {"message": resp.text.strip()}
