# /app/services/user_service.py

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core import security
from app.db import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Retrieves a user by their ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to retrieve.

    Returns:
        Optional[models.User]: The user object if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieves a user by their email address.

    Args:
        db (Session): The database session.
        email (str): The email of the user to retrieve.

    Returns:
        Optional[models.User]: The user object if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """

    Retrieves a user by their username.

    Args:
        db (Session): The database session.
        username (str): The username of the user to retrieve.

    Returns:
        Optional[models.User]: The user object if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Retrieves a paginated list of users.

    Args:
        db (Session): The database session.
        skip (int): The number of users to skip.
        limit (int): The maximum number of users to return.

    Returns:
        List[models.User]: A list of user objects.
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Creates a new user in the database.
    Hashes the password before saving.

    Args:
        db (Session): The database session.
        user_in (schemas.UserCreate): The user creation schema with plain password.

    Returns:
        models.User: The newly created user object.
    """
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[models.User]:
    """

    Authenticates a user by username and password.

    Args:
        db (Session): The database session.
        username (str): The user's username.
        password (str): The user's plain text password.

    Returns:
        Optional[models.User]: The user object if authentication is successful, otherwise None.
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user
