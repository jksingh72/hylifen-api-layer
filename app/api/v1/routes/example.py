from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user


class ExampleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ExampleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("", response_model=list[ExampleResponse])
async def list_examples(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all example records.
    Requires a valid Google JWT (or AUTH_BYPASS_ENABLED=true).
    """
    # TODO: replace with real DB query, e.g.:
    # result = await db.execute(select(ExampleRecord))
    # return result.scalars().all()
    return []


@router.post("", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    payload: ExampleCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new example record.
    Requires a valid Google JWT (or AUTH_BYPASS_ENABLED=true).
    """
    # TODO: replace with real DB insert, e.g.:
    # record = ExampleRecord(name=payload.name, description=payload.description)
    # db.add(record)
    # await db.flush()
    # return record
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet",
    )
