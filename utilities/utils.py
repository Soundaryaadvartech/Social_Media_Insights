import os
from dotenv import load_dotenv

load_dotenv()

def get_credentials(business: str):
    """Fetch brand-specific credentials dynamically."""
    if business.lower() == "zing":
        return {
            "BASE_URL": os.getenv("ZING_BASE_URL"),
            "INSTA_ACCESS_TOKEN": os.getenv("ZING_INSTA_ACCESS_TOKEN"),
            "INSTAGRAM_ACCOUNT_ID": os.getenv("ZING_INSTAGRAM_ACCOUNT_ID"),
            "ACCESS_TOKEN": os.getenv("ZING_ACCESS_TOKEN"),
            "META_APP_ID": os.getenv("ZING_META_APP_ID"),
            "META_APP_SECRET": os.getenv("ZING_META_APP_SECRET"),
            "LONG_LIVED_TOKEN": os.getenv("ZING_LONG_LIVED_TOKEN"),
        }
    elif business.lower() == "prathiksham":
        return {
            "BASE_URL": os.getenv("PKM_BASE_URL"),
            "INSTA_ACCESS_TOKEN": os.getenv("PKM_INSTA_ACCESS_TOKEN"),
            "INSTAGRAM_ACCOUNT_ID": os.getenv("PKM_INSTAGRAM_ACCOUNT_ID"),
            "ACCESS_TOKEN": os.getenv("PKM_ACCESS_TOKEN"),
            "META_APP_ID": os.getenv("PKM_META_APP_ID"),
            "META_APP_SECRET": os.getenv("PKM_META_APP_SECRET"),
            "LONG_LIVED_TOKEN": os.getenv("PKM_LONG_LIVED_TOKEN"),
        }
    elif business.lower() == "beelittle":
        return {
            "BASE_URL": os.getenv("BLT_BASE_URL"),
            "INSTA_ACCESS_TOKEN": os.getenv("BLT_INSTA_ACCESS_TOKEN"),
            "INSTAGRAM_ACCOUNT_ID": os.getenv("BLT_INSTAGRAM_ACCOUNT_ID"),
            "ACCESS_TOKEN": os.getenv("BLT_ACCESS_TOKEN"),
            "META_APP_ID": os.getenv("BLT_META_APP_ID"),
            "META_APP_SECRET": os.getenv("BLT_META_APP_SECRET"),
            "LONG_LIVED_TOKEN": os.getenv("BLT_LONG_LIVED_TOKEN"),
        }
    elif business.lower() == "adoreaboo":
        return {
            "BASE_URL": os.getenv("ADB_BASE_URL"),
            "INSTA_ACCESS_TOKEN": os.getenv("ADOREABOO_INSTA_ACCESS_TOKEN"),
            "INSTAGRAM_ACCOUNT_ID": os.getenv("ADOREABOO_INSTAGRAM_ACCOUNT_ID"),
            "ACCESS_TOKEN": os.getenv("ADOREABOO_ACCESS_TOKEN"),
            "META_APP_ID": os.getenv("ADB_META_APP_ID"),
            "META_APP_SECRET": os.getenv("ADB_META_APP_SECRET"),
            "LONG_LIVED_TOKEN": os.getenv("ADB_LONG_LIVED_TOKEN"),
        }
    else:
        raise ValueError("Invalid business name provided")
