from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

# from app.api.dependencies import oauth2_scheme
from app.core.config import settings
from app.core.exceptions import InvalidTokenException
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/users/login"
)

async def get_current_user(
        token : str = Depends(oauth2_scheme),
        db : AsyncSession = Depends(get_db)
) -> User:

    try:
        # Decode and verify JWT

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        # Extract user ID
        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenException()

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise InvalidTokenException()

    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id==user_id)
    )

    user = result.scalar_one_or_none()

    #  Ensure user exists
    if user is None:
        raise InvalidTokenException()

    # Return authenticated user
    return user
    