from typing import Dict
from telegram import Update

def extract_user_data_from_update(update: Update) -> Dict:
    """Extract user information from the Update instance."""
    user = update.effective_user.to_dict()

    return {
        "user_id": user.get("id"),
        "is_blocked_bot": False,
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "language_code": user.get("language_code"),
    }
