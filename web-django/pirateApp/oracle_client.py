import requests
from django.conf import settings


class OracleAPIError(Exception):
    pass


def fetch_next_direction(oracle_id: str, instruction_number: int) -> dict:
    """
    oracle_id: "set-sail", "strong-winds", etc. (vine din nextID)
    instruction_number: 1,2,3,... (instruction_id query param)
    """

    base = getattr(settings, "ORACLE_BASE_URL", "").rstrip("/")
    if not base:
        raise OracleAPIError("ORACLE_BASE_URL nu e setat în settings.py")

    url = f"{base}/direction/{oracle_id}/"
    params = {"instruction_id": instruction_number}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise OracleAPIError(f"Eroare request către Oracle: {e}")
    except ValueError:
        raise OracleAPIError("Oracle a returnat ceva ce nu e JSON valid")


def check_password(code: str) -> dict:
    """
    code = "abcd" (4 cifre)
    Oracle route: check-password/abcd
    """
    base = settings.ORACLE_BASE_URL.rstrip("/")
    url = f"{base}/check-password/{code}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        # uneori oracle poate întoarce text simplu; încercăm json, altfel text
        try:
            return r.json()
        except ValueError:
            return {"message": r.text}
    except requests.RequestException as e:
        raise OracleAPIError(f"Eroare request către Oracle: {e}")