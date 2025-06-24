import unicodedata
from PIL import Image, ImageDraw, ImageFont
import hashlib
import tldextract

def check_homoglyph(url):
    # Unicode normalization
    normalized = unicodedata.normalize("NFKC", url).lower()
    if normalized != url.lower():
        return True, "Homoglyph detected: Unicode characters used."
    
    # Visual rendering check
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    img = Image.new("RGB", (200, 50), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    draw.text((10, 10), domain, fill="black", font=font)
    img_hash = hashlib.md5(img.tobytes()).hexdigest()
    
    # Compare with known legit domain (e.g., google.com)
    legit_img = Image.new("RGB", (200, 50), color="white")
    legit_draw = ImageDraw.Draw(legit_img)
    legit_draw.text((10, 10), "google.com", fill="black", font=font)
    legit_hash = hashlib.md5(legit_img.tobytes()).hexdigest()
    
    # Enhanced homoglyph patterns (Cyrillic, Greek, Latin)
    homoglyph_patterns = [
        ("а", "a"),  # Cyrillic 'a'
        ("ο", "o"),  # Greek 'omicron'
        ("і", "i"),  # Cyrillic 'i'
    ]
    for spoof, legit in homoglyph_patterns:
        if spoof in domain.lower():
            return True, f"Homoglyph detected: Character '{spoof}' mimics '{legit}'."
    
    if img_hash == legit_hash and domain != "google.com":
        return True, "Homoglyph detected: Visually mimics google.com."
    
    return False, ""