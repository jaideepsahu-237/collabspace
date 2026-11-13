from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

from app.db.session import get_db

from app.api.routes.tenants import router as tenants_router
from app.api.routes.users import router as user_router

app = FastAPI(title="CollabSpace API")

app.include_router(tenants_router)
app.include_router(user_router)

@app.get("/health")
async def health_check():
    return {"Status" : "OK"}


@app.get("/health/db")
async def database_health_check(
    db : AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()

        if value == 1:
            return{
                "status" : "OK",
                "databse" : "connected"
            }

        raise HTTPException(
            status_code=500,
            detail="Unexpected databse response"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(exc)}"
        ) from exc  

@app.exception_handler(AppException)
async def tenant_not_found_handler(
        request : Request,
        exc : AppException
):
    return JSONResponse(
        status_code=404,
        content={
            "success" : False,
            "message" : exc.message,
        }
    )