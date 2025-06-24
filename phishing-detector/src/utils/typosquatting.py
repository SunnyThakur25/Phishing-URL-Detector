from Levenshtein import distance

def check_typosquatting(domain, legit_domains):
    for legit in legit_domains:
        if distance(domain.lower(), legit) < 3:
            return True, f"Typosquatting detected: Similar to {legit}"
    return False, ""