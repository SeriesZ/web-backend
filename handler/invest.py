from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import get_db
from model.invest import Investment, Investor
from model.user import RoleEnum, User
from schema.invest import InvestmentRequest, InvestorRequest

router = APIRouter(tags=["invest"])


@router.post("/investments", status_code=status.HTTP_201_CREATED)
async def create_investment(
    request: InvestmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (RoleEnum.INVESTOR, RoleEnum.ADMIN):
        raise HTTPException(
            status_code=403, detail="투자자 권한이 필요합니다."
        )

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
    clause = [Investment.id == investment_id]
    if current_user.role == RoleEnum.INVESTOR:
        clause += [Investment.investor_id == current_user.investor_id]
    elif current_user.role == RoleEnum.ADMIN:
        pass
    else:
        raise HTTPException(
            status_code=403, detail="투자자 권한이 필요합니다."
        )

    result = await db.execute(
        update(Investment)
        .where(*clause)
        .values(**request.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "투자 정보가 성공적으로 수정되었습니다."}


@router.delete(
    "/investments/{investment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_investment(
    investment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clause = [Investment.id == investment_id]
    if current_user.role == RoleEnum.INVESTOR:
        clause += [Investment.investor_id == current_user.investor_id]
    elif current_user.role == RoleEnum.ADMIN:
        pass
    else:
        raise HTTPException(
            status_code=403, detail="투자자 권한이 필요합니다."
        )

    result = await db.execute(
        update(Investment).where(*clause).values(in_use=False)
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
    check_investor_permission(current_user)

    async with db.begin():
        # 투자자 생성 및 추가
        investor = Investor(**request.dict())
        db.add(investor)
        await db.flush()
        await db.refresh(investor)
        # 사용자 업데이트
        current_user.investor_id = investor.id

    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/investor/{investor_id}", status_code=status.HTTP_200_OK)
async def update_investor(
    investor_id: str,
    request: InvestorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_investor_permission(current_user, investor_id=investor_id)

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
    check_investor_permission(current_user, investor_id=investor_id)

    result = await db.execute(
        update(Investor).where(Investor.id == investor_id).values(in_use=False)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Investor not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def check_investor_permission(
    current_user: User, investor_id: Optional[str] = None
):
    if current_user.role == RoleEnum.ADMIN:
        return
    if current_user.role != RoleEnum.INVESTOR:
        raise HTTPException(
            status_code=403, detail="투자자 권한이 필요합니다."
        )
    if investor_id and current_user.investor_id != investor_id:
        raise HTTPException(
            status_code=403, detail="해당 투자사에 대한 권한이 없습니다."
        )
