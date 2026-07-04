from typing import Optional

from config import Config
from db.repositories import bot_state_repo, channel_repo, group_repo, user_repo
from db.session import get_session
from services.verse_ingestion_service import LAST_INGESTION_STATE_KEY


def register_incoming_message(chat: dict) -> None:
    """
    Called on every incoming update. Makes sure the sender (private user,
    group, or channel) is tracked in Postgres, so the scheduler's daily
    broadcast can reach anyone who has ever talked to the bot instead of
    relying solely on a static env var list.
    """
    chat_type = chat.get("type", "private")
    chat_id = chat.get("id")

    if chat_id is None:
        return

    with get_session() as session:
        if chat_type == "private":
            user_repo.get_or_create(
                session,
                user_id=chat_id,
                username=chat.get("username"),
                first_name=chat.get("first_name"),
            )
        elif chat_type in ("group", "supergroup"):
            group_repo.get_or_create(session, chat_id=chat_id, title=chat.get("title"))
        elif chat_type == "channel":
            channel_repo.get_or_create(
                session,
                chat_id=chat_id,
                title=chat.get("title"),
                username=chat.get("username"),
            )


def is_admin(user_id: int) -> bool:
    """A user is an admin if they're flagged in the DB or listed in
    ADMIN_USER_IDS (which is applied on startup, see bootstrap_admins)."""
    with get_session() as session:
        return user_repo.is_admin(session, user_id)


def bootstrap_admins() -> None:
    """Run once at startup: promote any configured ADMIN_USER_IDS."""
    admin_ids = Config.get_admin_ids()
    if not admin_ids:
        return

    with get_session() as session:
        for admin_id in admin_ids:
            user = user_repo.get_or_create(session, user_id=admin_id)
            user.is_admin = True


def seed_static_recipients() -> None:
    """
    Run once at startup: import CHANNEL_IDS / GROUP_IDS / USER_IDS from
    the env into Postgres, so existing deployments don't lose their
    configured recipients when switching to DB-backed tracking.
    """
    with get_session() as session:
        for channel_id in Config.get_seed_channel_ids():
            channel_repo.get_or_create(session, chat_id=channel_id)

        for group_id in Config.get_seed_group_ids():
            group_repo.get_or_create(session, chat_id=group_id)

        for user_id in Config.get_seed_user_ids():
            user_repo.get_or_create(session, user_id=user_id)


def get_stats() -> dict:
    with get_session() as session:
        return {
            "users": user_repo.count(session),
            "channels": channel_repo.count(session),
            "groups": group_repo.count(session),
            "last_verse_ingestion": bot_state_repo.get(session, LAST_INGESTION_STATE_KEY),
        }
