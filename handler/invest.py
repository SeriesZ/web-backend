from typing import List

from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer
from model.invest import Investment, Investor
from model.user import User
from schema.invest import (InvestmentRequest, InvestmentResponse,
                           InvestorRequest, InvestorResponse)
from service.repository import CrudRepository, get_repository

router = APIRouter(tags=["투자"])


@router.post("/investment", response_model=InvestmentResponse)
async def create_investment(
    request: InvestmentRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    # FIXME investor를 group으로 바꾸던가 해야함
    # if not current_user.group_id == request.investor_id:
    #     raise HTTPException(status_code=403, detail="Permission denied")
    investment = Investment(**request.dict())
    investment = await repo.create(investment)
    await enforcer.add_policies(
        [
            (current_user.id, investment.id, "write"),
            (current_user.group_id, investment.id, "write"),
        ]
    )
    return InvestmentResponse.model_validate(investment)


@router.put("/investment/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: str,
    request: InvestmentRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    # if not enforcer.enforce(current_user.id, investment_id, "write"):
    #     raise HTTPException(status_code=403, detail="Permission denied")
    investment = Investment(id=investment_id, **request.dict())
    investment = await repo.update(investment)
    return InvestmentResponse.model_validate(investment)


@router.delete(
    "/investment/{investment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_investment(
    investment_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    # if not enforcer.enforce(current_user.id, investment_id, "write"):
    #     raise HTTPException(status_code=403, detail="Permission denied")
    await repo.delete(Investment(id=investment_id))


@router.get("/investors", response_model=List[InvestorResponse])
async def get_investors(
    offset: int = 0,
    limit: int = 10,
    repo: CrudRepository = Depends(get_repository),
):
    investors = await repo.fetch_all(Investor, offset, limit)
    return [InvestorResponse.model_validate(i) for i in investors]


@router.get("/investor/{investor_id}", response_model=InvestorResponse)
async def get_investor(
    investor_id: str,
    repo: CrudRepository = Depends(get_repository),
):
    investor = await repo.find_by_id(Investor, investor_id)
    return InvestorResponse.model_validate(investor)


@router.post("/investor", response_model=InvestorResponse)
async def create_investor(
    request: InvestorRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    investor = Investor(**request.dict())
    investor = await repo.create(investor)
    await enforcer.add_policies(
        [
            (investor.id, investor.id, "write"),  # group 사용자 권한
        ]
    )
    return InvestorResponse.model_validate(investor)


@router.put("/investor/{investor_id}", response_model=InvestorResponse)
async def update_investor(
    investor_id: str,
    request: InvestorRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    # if not enforcer.enforce(current_user.group_id, investor_id, "write"):
    #     raise HTTPException(status_code=403, detail="Permission denied")

    investor = Investor(id=investor_id, **request.dict())
    investor = await repo.update(investor)
    return InvestorResponse.model_validate(investor)


@router.delete(
    "/investor/{investor_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_investor(
    investor_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    # if not enforcer.enforce(current_user.group_id, investor_id, "write"):
    #     raise HTTPException(status_code=403, detail="Permission denied")
    await repo.delete(Investor(id=investor_id))
