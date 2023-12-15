import logging
from datetime import datetime
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .. import entities, models
from ..database import get_db

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/systems", tags=["Systems"])


@router.get("", response_model=list[models.System])
async def get_systems(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(entities.System))).scalars().all()


async def get_supreme_commander_name(
    email: EmailStr = Query(..., description="Email of the supreme commander"),
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://jsonplaceholder.typicode.com/users?email={email}"
        )
        if response.status_code == 200:
            user_data = response.json()
            if user_data:
                return user_data[0]["name"]
    raise HTTPException(
        status_code=404, detail=f"Supreme commander not found for email: {email}"
    )


@router.post("", response_model=models.System)
async def create_system(
    request: models.CreateSystem,
    supreme_commander_name: EmailStr = Depends(get_supreme_commander_name),
    db: AsyncSession = Depends(get_db),
):
    system = entities.System()
    system.id = uuid4()
    system.name = request.name
    system.supreme_commander = request.supreme_commander
    system.supreme_commander_name = supreme_commander_name
    system.date_created = datetime.now()

    db.add(system)
    await db.commit()

    return system
