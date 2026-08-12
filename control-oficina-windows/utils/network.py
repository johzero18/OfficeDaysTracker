import subprocess
import re


def get_default_gateway():
    """Obtiene el default gateway en Windows usando route print."""
    try:
        result = subprocess.run(
            ["route", "print", "-4", "0.0.0.0"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if (
                len(parts) >= 3
                and parts[0] == "0.0.0.0"
                and parts[1] == "0.0.0.0"
            ):
                return parts[2]
        return None
    except Exception:
        return None


def validate_ip(gateway: str) -> bool:
    """Valida que una dirección IP tenga formato x.x.x.x con cada octeto 0-255."""
    parts = gateway.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True
