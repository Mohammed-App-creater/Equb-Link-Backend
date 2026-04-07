"""
Predefined banks / wallets for equb owner payout details.
Replace logo_url values with your CDN or static asset URLs when ready.
Telebirr uses code TBR (not ABY) so it does not collide with Abay Bank.
"""

from typing import Any, Dict, List, Optional

# Each entry: display name, stable code, optional logo URL
ETHIOPIAN_BANKS: List[Dict[str, Any]] = [
    {
        "code": "CBE",
        "name": "Commercial Bank of Ethiopia",
        "logo_url": "",
    },
    {
        "code": "AWB",
        "name": "Awash International Bank",
        "logo_url": "",
    },
    {
        "code": "BOA",
        "name": "Bank of Abyssinia",
        "logo_url": "",
    },
    {
        "code": "DB",
        "name": "Dashen Bank",
        "logo_url": "",
    },
    {
        "code": "ZB",
        "name": "Zemen Bank",
        "logo_url": "",
    },
    {
        "code": "AMH",
        "name": "Amhara Bank",
        "logo_url": "",
    },
    {
        "code": "ABY",
        "name": "Abay Bank",
        "logo_url": "",
    },
    {
        "code": "TBR",
        "name": "Telebirr",
        "logo_url": "",
    },
]

_BANK_BY_CODE = {b["code"]: b for b in ETHIOPIAN_BANKS}


def get_bank_by_code(code: str) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    return _BANK_BY_CODE.get(code.upper())


def is_valid_bank_code(code: str) -> bool:
    return bool(code and code.upper() in _BANK_BY_CODE)
