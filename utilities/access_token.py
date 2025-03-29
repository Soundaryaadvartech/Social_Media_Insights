import os
import requests
import time
from dotenv import load_dotenv, set_key
from fastapi import HTTPException, status
from utilities.utils import get_credentials

def refresh_access_token(app_id: str, app_secret: str, long_lived_token: str):
    """
    Refresh the long-lived access token using Meta's Graph API.
    """
    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": long_lived_token,
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")
    
    data = response.json()
    return data.get("access_token")

def is_access_token_expired(access_token: str, business: str) -> bool:
    """
    Check if the access token has expired by making a test request to the Instagram API.
    Returns True if expired, False if valid.
    """
    credentials = get_credentials(business)
    BASE_URL = credentials["BASE_URL"]
    INSTAGRAM_ACCOUNT_ID = credentials["INSTAGRAM_ACCOUNT_ID"]
    ACCESS_TOKEN = credentials["ACCESS_TOKEN"]

    test_url = f"{BASE_URL}{INSTAGRAM_ACCOUNT_ID}?fields=id&access_token={ACCESS_TOKEN}"
    response = requests.get(test_url)
   # Check for 401 Unauthorized (token expired)
    if response.status_code == 401:
        return True
    
    # Check for 400 Bad Request with expired token message
    if response.status_code == 400:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "")
            # If the error message indicates token expiration
            if "expired" in error_message.lower():
                return True
        except ValueError:
            pass  # In case response is not in JSON format or doesn't contain error info
    
    return False

def generate_new_long_lived_token(business) -> str:
    """
    Generate a new long-lived token using the current short-lived token.
    Returns the new long-lived token.
    """
    credentials = get_credentials(business)
    ACCESS_TOKEN = credentials["ACCESS_TOKEN"]
    APP_ID = credentials["META_APP_ID"]
    APP_SECRET = credentials["META_APP_SECRET"]

    long_lived_token_key = f"{business.upper()}_LONG_LIVED_TOKEN"
    expiry_key = f"{business.upper()}_LONG_LIVED_TOKEN_EXPIRY"

    LONG_LIVED_TOKEN = os.getenv(long_lived_token_key, "")
    last_refreshed = int(os.getenv(expiry_key, 0))  # Last stored expiry timestamp

     # Check if 40 days have passed
    days_since_refresh = (int(time.time()) - last_refreshed) // (24 * 60 * 60)
    if days_since_refresh < 50:
        print(f"ℹ️ {business}: Long-lived token is still valid, skipping refresh.")
        return LONG_LIVED_TOKEN  # Return current token

    try:
        short_lived_token = ACCESS_TOKEN

        if not short_lived_token:
            raise Exception("Short-lived token not found in .env file.")
        
        url = f"https://graph.facebook.com/v21.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'fb_exchange_token': short_lived_token,  # The old short lived access token
        }

        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            new_token_data = response.json()
            new_long_lived_token = new_token_data.get("access_token")
            
            if new_long_lived_token:
                # Store new token and expiry time (60 days validity)
                expiry_timestamp = int(time.time()) + (60 * 24 * 60 * 60)
                # Update .env with brand-specific keys
                set_key('.env', long_lived_token_key, new_long_lived_token)
                set_key('.env', expiry_key, str(expiry_timestamp))
                load_dotenv()  # Reload environment variables

                print(f"✅ {business}: Successfully refreshed long-lived token.")
                return new_long_lived_token
            else:
                raise Exception("Failed to generate a new long-lived token.")
        else:
            raise Exception(f"Error generating new long-lived token: {response.text}")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate new long-lived token: {str(e)}"
        )