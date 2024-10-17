from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import get_db, enforcer
from model.financial import Financial
from model.user import User
from schema.financial import FinancialResponse, FinancialRequest

router = APIRouter(tags=["금융"])


@router.get("/financial/{ideation_id}", response_model=FinancialResponse)
async def get_financial(
        ideation_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    financial = await db.execute(
        select(Financial).where(Financial.ideation_id == ideation_id)
    )
    financial = financial.scalars().first()
    if not financial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financial not found",
        )
    return FinancialResponse.model_validate(financial)


@router.post("/financial", status_code=status.HTTP_201_CREATED)
async def create_financial(
        request: FinancialRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, request.ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    financial = Financial(
        **request.dict(),
        user_id=current_user.id,
    )
    db.add(financial)


@router.put("/financial", status_code=status.HTTP_200_OK)
async def update_financial(
        request: FinancialRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, request.ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    result = await db.execute(
        select(Financial).where(Financial.ideation_id == request.ideation_id)
    )
    financial = result.scalars().first()
    if not financial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financial not found",
        )
    for key, value in request.dict().items():
        setattr(financial, key, value)


@router.delete("/financial/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial(
        ideation_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    result = await db.execute(
        delete(Financial).where(Financial.ideation_id == ideation_id)
    )

    result = result.scalars().first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financial not found",
        )
