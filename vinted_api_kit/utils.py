from typing import Optional


def format_proxy_for_log(proxy: Optional[dict[str, str]]) -> str:
    """
    Format proxy address for logging.

    Args:
        proxy: Optional dict with keys like 'http' mapping to proxy URL.

    Returns:
        A string to show safe proxy information in logs.
    """
    if not proxy:
        return "local IP (no proxy configured)"
    proxy_value = proxy.get("http", "")
    if "@" in proxy_value:
        return proxy_value.split("@")[-1]
    elif proxy_value:
        return proxy_value
    else:
        return "unknown (invalid proxy format)"
