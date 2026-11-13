import os, json

BRAND_FILE = os.path.join(os.path.dirname(__file__), 'brand_settings.json')

DEFAULT_BRAND = {
    "company_name": "MOLOGIX",
    "company_tagline": "WMS",
    "warehouse_address": "Plot 42-B, Sundar Industrial Estate, Lahore",
    "phone": "+92-42-35290000",
    "ntn": "7845120-9",
    "strn": "32-77-8761-442-19",
    "logo_url": "",
    "invoice_footer": "Thank you for your business. Subject to Lahore jurisdiction. System generated GST invoice."
}

def get_brand():
    if os.path.exists(BRAND_FILE):
        try:
            with open(BRAND_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged = DEFAULT_BRAND.copy()
                merged.update({k: v for k, v in data.items() if v is not None})
                return merged
        except Exception:
            pass
    return DEFAULT_BRAND.copy()

def save_brand(data):
    cur = get_brand()
    cur.update(data)
    with open(BRAND_FILE, 'w', encoding='utf-8') as f:
        json.dump(cur, f, indent=2)
    return cur
