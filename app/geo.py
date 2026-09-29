import requests


def get_client_ip(request):
    """Get the real client IP, accounting for a reverse proxy (e.g. Railway, Nginx)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def resolve_location(ip_address):
    """Look up approximate city/country for an IP. Returns (city, country).
    Localhost/private IPs won't resolve to anything meaningful - that's expected
    until the app is deployed publicly."""
    if not ip_address or ip_address in ("127.0.0.1", "::1") or ip_address.startswith("192.168."):
        return None, None
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=2)
        data = resp.json()
        if data.get("status") == "success":
            return data.get("city"), data.get("country")
    except requests.RequestException:
        pass
    return None, None
