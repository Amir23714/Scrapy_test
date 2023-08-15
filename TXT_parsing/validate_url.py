
def validate_url(domains : list, blocked_domains : list):
    result = []
    for domain in domains:
        if domain not in blocked_domains:
            result.append(f"https://{domain}")

    return result