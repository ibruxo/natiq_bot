from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.channel import Channel


def get_by_id(session: Session, chat_id: int) -> Optional[Channel]:
    stmt = select(Channel).where(Channel.chat_id == chat_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    chat_id: int,
    title: Optional[str] = None,
    username: Optional[str] = None,
) -> Channel:
    channel = ch_id(session, chat_id)

    if channel:
        if title is not None:
            channel.title = title
        if username is not None:
            channel.username = username
        channel.is_active = True
        return channel

    channel = Channel(chat_id=chat_id, title=title, username=username)
    session.add(channel)
    session.flush()
    return channel


def deactivate(session: Session, chat_id: int) -> None:
    channel = get_by_id(session, chat_id)
    if channel:
        channel.is_active = False


def list_active_ids(session: Session) -> list[int]:
    stmt = select(Channel.chat_id).where(Channel.is_active.is_(True))
    return list(session.scalars(stmt))


def count(session: Session) -> int:
    return session.query(Channel).count()
