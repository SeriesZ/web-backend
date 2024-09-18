from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import get_db
from model.invest import Investor, InvestorUser, Investment
from model.user import User, RoleEnum
from schema.invest import InvestorRequest, InvestorResponse, InvestmentRequest

router = APIRouter(tags=["invest"])


@router.post("/investments", status_code=status.HTTP_201_CREATED)
async def create_investment(
        request: InvestmentRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role not in (RoleEnum.INVESTOR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자를 등록할 수 없습니다.")

    investor_users = await db.execute(
        select(InvestorUser)
        .where(
            InvestorUser.user_id == current_user.id,
            InvestorUser.investor_id == request.investor_id
        )
    )
    investor_users = investor_users.scalars().first()
    if not investor_users:
        raise HTTPException(status_code=403, detail="해당 유저에게 투자 권한이 없습니다.")

    investment = Investment(**request.dict())
    db.add(investment)
    await db.commit()
    await db.refresh(investment)
    return {"message": "투자가 성공적으로 등록되었습니다."}


@router.put("/investments/{investment_id}", status_code=status.HTTP_200_OK)
async def update_investment(
        investment_id: str,
        request: InvestmentRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role not in (RoleEnum.INVESTOR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자를 등록할 수 없습니다.")

    investor_users = await db.execute(
        select(InvestorUser)
        .where(
            InvestorUser.user_id == current_user.id,
            InvestorUser.investor_id == request.investor_id
        )
    )
    investor_users = investor_users.scalars().first()
    if not investor_users:
        raise HTTPException(status_code=403, detail="해당 유저에게 투자 수정 권한이 없습니다.")

    result = await db.execute(
        update(Investment)
        .where(Investment.id == investment_id)
        .values(**request.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "투자 정보가 성공적으로 수정되었습니다."}


@router.delete("/investments/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment(
        investment_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role not in (RoleEnum.INVESTOR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자를 삭제할 수 없습니다.")

    investment = await db.execute(
        select(Investment).where(Investment.id == investment_id)
    )
    investment = investment.scalars().first()

    investor_users = await db.execute(
        select(InvestorUser)
        .where(
            InvestorUser.user_id == current_user.id,
            InvestorUser.investor_id == investment.investor_id
        )
    )
    investor_users = investor_users.scalars().first()
    if not investor_users:
        raise HTTPException(status_code=403, detail="해당 유저에게 투자 삭제 권한이 없습니다.")

    result = await db.execute(
        update(Investment)
        .where(Investment.id == investment_id)
        .values(in_use=False)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "투자 정보가 성공적으로 삭제되었습니다."}


@router.post("/investor", status_code=status.HTTP_201_CREATED)
async def create_investor(
        request: InvestorRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role not in (RoleEnum.INVESTOR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자자 정보를 등록할 수 없습니다.")

    investor = Investor(**request.dict())
    db.add(investor)
    await db.commit()
    await db.refresh(investor)
    return {"message": "투자자 정보가 성공적으로 등록되었습니다."}


@router.put("/investor/{investor_id}", status_code=status.HTTP_200_OK)
async def update_investor(
        investor_id: str,
        request: InvestorRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != RoleEnum.INVESTOR:
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자자 정보를 수정할 수 없습니다.")

    investor_user = await db.execute(
        select(InvestorUser)
        .where(
            InvestorUser.investor_id == investor_id,
            InvestorUser.user_id == current_user.id
        )
    )
    if not investor_user:
        raise HTTPException(status_code=403, detail="투자자 정보 수정 권한이 없습니다.")

    result = await db.execute(
        update(Investor)
        .where(Investor.id == investor_id)
        .values(**request.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    return {"message": "투자자 정보가 성공적으로 수정되었습니다."}


@router.delete("/investor/{investor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investor(
        investor_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != RoleEnum.INVESTOR:
        raise HTTPException(status_code=403, detail="투자자가 아니면 투자자 정보를 삭제할 수 없습니다.")

    investor_user = await db.execute(
        select(InvestorUser)
        .where(
            InvestorUser.investor_id == investor_id,
            InvestorUser.user_id == current_user.id
        )
    )
    if not investor_user:
        raise HTTPException(status_code=403, detail="투자자 정보 삭제 권한이 없습니다.")

    result = await db.execute(
        update(Investor)
        .where(Investor.id == investor_id)
        .values(in_use=False)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    return {"message": "투자자 정보가 성공적으로 삭제되었습니다."}


@router.post("/investor_user/{investor_id}", status_code=status.HTTP_201_CREATED)
async def create_investor_user(
        investor_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # 투자자 조회
    investor = await db.execute(select(Investor).where(Investor.id == investor_id))
    investor = investor.scalars().first()

    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")

    # 중간 테이블에 추가
    investor_user = InvestorUser(user_id=current_user.id, investor_id=investor_id)
    db.add(investor_user)

    await db.commit()
    return {"message": "투자자와 사용자가 성공적으로 추가되었습니다."}


@router.delete("/investor_user/{investor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investor_user(
        investor_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        update(InvestorUser)
        .where(
            InvestorUser.investor_id == investor_id,
            InvestorUser.user_id == current_user.id
        )
        .values(in_use=False)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="InvestorUser not found")

    await db.commit()
    return {"message": "투자자와 사용자가 성공적으로 삭제되었습니다."}


@router.get("/investor_user/me", response_model=List[InvestorResponse])
async def get_my_investors(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    query = select(Investor).join(InvestorUser).where(InvestorUser.user_id == current_user.id)
    investors = await db.execute(query)
    investors = investors.scalars().all()
    return [InvestorResponse.from_orm(investor) for investor in investors]
