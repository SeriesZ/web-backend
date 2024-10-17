from typing import List

from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer, get_db
from model.invest import Investment, Investor
from model.user import User
from schema.invest import InvestmentRequest, InvestorRequest, InvestorResponse

router = APIRouter(tags=["투자"])


@router.post("/investments", status_code=status.HTTP_201_CREATED)
async def create_investment(
        request: InvestmentRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    investment = Investment(**request.dict())
    db.add(investment)
    await db.commit()
    await db.refresh(investment)
    await enforcer.add_policies(
        [
            (current_user.id, investment.id, "write"),
            (current_user.group_id, investment.id, "write"),
        ]
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/investments/{investment_id}", status_code=status.HTTP_200_OK)
async def update_investment(
        investment_id: str,
        request: InvestmentRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, investment_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        update(Investment)
        .where(Investment.id == investment_id)
        .values(**request.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/investments/{investment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_investment(
        investment_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, investment_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        delete(Investment).where(Investment.id == investment_id)
    )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/investors", response_model=List[InvestorResponse])
async def get_investors(
        offset: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
):
    investors = await db.execute(select(Investor))
    investors = investors.scalars().all()
    return [InvestorResponse.model_validate(i) for i in investors]


@router.get("/investor/{investor_id}", response_model=InvestorResponse)
async def get_investor(
        investor_id: str,
        db: AsyncSession = Depends(get_db),
):
    investor = await db.execute(select(Investor).where(Investor.id == investor_id))
    investor = investor.scalar()
    if investor is None:
        raise HTTPException(status_code=404, detail="Investor not found")
    return InvestorResponse.model_validate(investor)


@router.post("/investor", status_code=status.HTTP_201_CREATED)
async def create_investor(
        request: InvestorRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    async with db.begin():
        # 투자자 생성 및 추가
        investor = Investor(**request.dict())
        db.add(investor)
        await db.flush()
        await db.refresh(investor)
    await enforcer.add_policies(
        [
            (investor.id, investor.id, "write"),  # group 사용자 권한
        ]
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/investor/{investor_id}", status_code=status.HTTP_200_OK)
async def update_investor(
        investor_id: str,
        request: InvestorRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.group_id, investor_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        update(Investor)
        .where(Investor.id == investor_id)
        .values(**request.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/investor/{investor_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_investor(
        investor_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.group_id, investor_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        delete(Investor).where(Investor.id == investor_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
