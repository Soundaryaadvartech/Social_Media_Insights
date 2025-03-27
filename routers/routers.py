import traceback
from datetime import datetime, timezone
import requests
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from database.models import SocialMedia
from utilities.access_token import refresh_access_token, is_access_token_expired, generate_new_long_lived_token
from database.database import get_db
from utilities.utils import get_credentials

router = APIRouter()

@router.get("/fetch_insights")
def fetch_insights(business: str, db: Session = Depends(get_db())):
    """
    Fetch a summarized version of Instagram insights for the specified business.
    Automatically refreshes access token if needed.
    """
    try:
        # Get credentials dynamically based on business_code
        db = next(get_db(business))
        credentials = get_credentials(business)
        BASE_URL = credentials["BASE_URL"]
        ACCESS_TOKEN = credentials["ACCESS_TOKEN"]
        INSTAGRAM_ACCOUNT_ID = credentials["INSTAGRAM_ACCOUNT_ID"]
        APP_ID = credentials["META_APP_ID"]
        APP_SECRET = credentials["META_APP_SECRET"]
        LONG_LIVED_TOKEN = credentials["LONG_LIVED_TOKEN"]

        # Refresh the short-lived token if expired
        if is_access_token_expired(ACCESS_TOKEN, business):
            try:
                refreshed_token = refresh_access_token(APP_ID, APP_SECRET, LONG_LIVED_TOKEN)
                ACCESS_TOKEN = refreshed_token
            except Exception:
                try:
                    new_long_lived_token = generate_new_long_lived_token(business)
                    refreshed_token = refresh_access_token(APP_ID, APP_SECRET, new_long_lived_token)
                    ACCESS_TOKEN = refreshed_token
                except Exception as gen_error:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to generate new long-lived token: {str(gen_error)}"
                    )

        # Fetch Instagram account details
        account_url = f"{BASE_URL}{INSTAGRAM_ACCOUNT_ID}?fields=id,username,followers_count&access_token={ACCESS_TOKEN}"
        account_response = requests.get(account_url, timeout=120)
        if account_response.status_code != 200:
            raise HTTPException(
                status_code=account_response.status_code,
                detail=f"Failed to fetch account details: {account_response.text}"
            )
        account_data = account_response.json()

        # Fetch insights
        insights_url = f"{BASE_URL}{INSTAGRAM_ACCOUNT_ID}/insights?metric=reach,accounts_engaged,website_clicks&period=day&metric_type=total_value&access_token={ACCESS_TOKEN}"
        insights_response = requests.get(insights_url, timeout=120)
        if insights_response.status_code != 200:
            raise HTTPException(
                status_code=insights_response.status_code,
                detail=f"Failed to fetch insights: {insights_response.text}"
            )
        insights_data = insights_response.json()

        # Extract insights
        reach, accounts_engaged, website_clicks = None, None, None
        for item in insights_data.get("data", []):
            if item.get("name") == "reach":
                reach = item.get("values", [{}])[-1].get("value")
            if item.get("name") == "accounts_engaged":
                accounts_engaged = item.get("values", [{}])[-1].get("value")
            if item.get("name") == "website_clicks":
                website_clicks = item.get("values", [{}])[-1].get("value")

        # Combine results
        result = {
            "username": account_data.get("username"),
            "followers_count": account_data.get("followers_count"),
            "reach": reach,
            "accounts_engaged": accounts_engaged,
            "website_clicks": website_clicks,
        }

        # Calculate the sum of existing records
        existing_sums = db.query(
            func.sum(SocialMedia.followers).label("total_followers"),
            func.sum(SocialMedia.reach).label("total_reach"),
            func.sum(SocialMedia.accounts_engaged).label("total_accounts_engaged"),
            func.sum(SocialMedia.website_clicks).label("total_website_clicks"),
        ).first()

        # Extract values or default to 0
        total_followers = existing_sums.total_followers or 0
        total_reach = existing_sums.total_reach or 0
        total_accounts_engaged = existing_sums.total_accounts_engaged or 0
        total_website_clicks = existing_sums.total_website_clicks or 0

        # Calculate the differences (new data - sum of existing records)
        new_followers = result["followers_count"] - total_followers
        new_reach = result["reach"] - total_reach
        new_accounts_engaged = result["accounts_engaged"] - total_accounts_engaged
        new_website_clicks = result["website_clicks"] - total_website_clicks

        # Get today's date in UTC
        today_date = datetime.now(timezone.utc).date()

        # Check if a record for today already exists
        existing_record = db.query(SocialMedia).filter(func.date(SocialMedia.created_ts) == today_date).first()

        if existing_record:
            # Update today's record with calculated differences
            existing_record.followers += new_followers
            existing_record.reach += new_reach
            existing_record.accounts_engaged += new_accounts_engaged
            existing_record.website_clicks += new_website_clicks
            existing_record.updated_ts = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_record)
        else:
            # Insert a new record with calculated differences
            socialmedia_analytics = SocialMedia(
                username=result["username"],
                followers=new_followers,
                reach=new_reach,
                accounts_engaged=new_accounts_engaged,
                website_clicks=new_website_clicks,
                created_ts=datetime.now(timezone.utc),
                updated_ts=datetime.now(timezone.utc),
            )
            db.add(socialmedia_analytics)
            db.commit()
            db.refresh(socialmedia_analytics)

        return JSONResponse(content=result)

    except HTTPException as e:
        db.rollback()
        traceback.print_exc()
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Something went wrong."})
