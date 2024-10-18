from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer, get_db
from model.finance import Finance
from model.user import User
from schema.finance import FinanceRequest, FinanceResponse

router = APIRouter(tags=["금융"])


@router.get("/finance/{ideation_id}", response_model=FinanceResponse)
async def get_finance(
    ideation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    finance = await db.execute(
        select(Finance).where(Finance.ideation_id == ideation_id)
    )
    finance = finance.scalars().first()
    if not finance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="finance not found",
        )
    return FinanceResponse.model_validate(finance)


@router.post("/finance", status_code=status.HTTP_201_CREATED)
async def create_finance(
    request: FinanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, request.ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    finance = Finance(
        **request.dict(),
        user_id=current_user.id,
    )
    db.add(finance)


@router.put("/finance", status_code=status.HTTP_200_OK)
async def update_finance(
    request: FinanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, request.ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    result = await db.execute(
        select(Finance).where(Finance.ideation_id == request.ideation_id)
    )
    finance = result.scalars().first()
    if not finance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="finance not found",
        )
    for key, value in request.dict().items():
        setattr(finance, key, value)


@router.delete(
    "/finance/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_finance(
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
        delete(Finance).where(Finance.ideation_id == ideation_id)
    )

    result = result.scalars().first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="finance not found",
        )
