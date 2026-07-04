from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.user import User


def get_by_id(session: Session, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    return session.scalar(stmt)


def get_or_create(
    session: Session,
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
) -> User:
    user = get_by_id(session, user_id)

    if user:
        # Keep profile info fresh.
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        return user

    user = User(
        user_id=user_id,
        username=username,
        first_name=first_name,
    )
    session.add(user)
    session.flush()
    return user


def set_admin(session: Session, user_id: int, is_admin: bool = True) -> Optional[User]:
    user = get_by_id(session, user_id)
    if user:
        user.is_admin = is_admin
    return user


def is_admin(session: Session, user_id: int) -> bool:
    user = get_by_id(session, user_id)
    return bool(user and user.is_admin)


def list_active_ids(session: Session) -> list[int]:
    stmt = select(User._user_id).where(User.is_active.is_(True))
    return list(session.scalars(stmt))


def count(session: Session) -> int:
    return session.query(User).count()
