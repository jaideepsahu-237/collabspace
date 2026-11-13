from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantResponse

router = APIRouter(
    prefix="/api/tenants",
    tags=["Tenants"],
)

@router.get("/", response_model=list[TenantResponse])
async def get_tenants(
        db : AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Tenant).order_by(Tenant.name)
    )

    tenants = result.scalars().all()

    return tenants