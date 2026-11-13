from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

from app.core.exceptions import TenantNotFoundException, UserAlreadyExistsException

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED
)
async def register_user(
        user_data : UserCreate,
        db : AsyncSession = Depends(get_db)
):
    # 1. Check whether tenant exists
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == user_data.tenant_id)
    )

    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise TenantNotFoundException(user_data.tenant_id)

    # 2. Check whether email already exists
    email_result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    existing_user = email_result.scalar_one_or_none()

    if existing_user:
        raise UserAlreadyExistsException(user_data.email)

    # 3. Hash password
    hashed_password = hash_password(user_data.password)

    # 4. Create user object

    new_user = User(
        name = user_data.name,
        email = user_data.email,
        password_hash = hashed_password,
        tenant_id = user_data.tenant_id
    )

    # 5. Save user in database
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise UserAlreadyExistsException(user_data.email)

    return new_user

