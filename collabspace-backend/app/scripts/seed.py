from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.tenant import Tenant

TENANTS = [
    "Acme Corp",
    "TechNova"
]

async def seed_tenants():
    async with SessionLocal() as session:
        for tenant_name in TENANTS:
            result = await session.execute(
                select(Tenant).where(Tenant.name == tenant_name)
            )
            tenant = result.scalar_one_or_none()

            if tenant is None:
                session.add(Tenant(name=tenant_name))
                print(f"Created tenant: {tenant_name}")
            else:
                print(f"Tenant already exists: {tenant_name}")

        await session.commit()

if __name__ == '__main__':
    import asyncio
    import selectors

    asyncio.run(seed_tenants(),
                loop_factory=lambda : asyncio.SelectorEventLoop(selectors.SelectSelector()))

