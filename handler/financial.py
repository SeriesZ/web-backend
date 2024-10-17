from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import get_db, enforcer
from model.financial import Financial
from model.user import User
from schema.financial import FinancialResponse

router = APIRouter(tags=["금융"])


@router.get("/financial/{id}", response_model=FinancialResponse)
async def get_financial(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    financial = await db.execute(
        select(Financial).where(Financial.id == id)
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
        request: Financial,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    financial = Financial(
        **request.dict(),
        user_id=current_user.id,
    )
    db.add(financial)
    await db.refresh(financial)
    await enforcer.add_policies(
        [
            (current_user.id, financial.id, "write"),
        ]
    )


@router.put("/financial/{id}", status_code=status.HTTP_200_OK)
async def update_financial(
        id: int,
        request: Financial,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    result = await db.execute(
        select(Financial).where(Financial.id == id)
    )
    financial = result.scalars().first()
    if not financial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financial not found",
        )
    for key, value in request.dict().items():
        setattr(financial, key, value)


@router.delete("/financial/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    result = await db.execute(
        delete(Financial).where(Financial.id == id)
    )

    result = result.scalars().first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financial not found",
        )
