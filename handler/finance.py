from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer
from model.finance import Finance
from model.user import User
from schema.finance import FinanceRequest, FinanceResponse
from service.repository import CrudRepository, get_repository

router = APIRouter(tags=["금융"])


@router.get("/finance/{ideation_id}", response_model=FinanceResponse)
async def get_finance(
    ideation_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    finance = await repo.find_by_id(
        Finance, ideation_id, field_name="ideation_id"
    )
    return FinanceResponse.model_validate(finance)


@router.post("/finance", response_model=FinanceResponse)
async def create_finance(
    request: FinanceRequest,
    repo: CrudRepository = Depends(get_repository),
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
    finance = await repo.create(finance)
    return FinanceResponse.model_validate(finance)


@router.put("/finance", response_model=FinanceResponse)
async def update_finance(
    request: FinanceRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, request.ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )

    finance = Finance(**request.dict())
    finance = await repo.update(finance, field_name="ideation_id")
    return FinanceResponse.model_validate(finance)


@router.delete(
    "/finance/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_finance(
    ideation_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied",
        )
    await repo.delete(Finance(ideation_id=ideation_id))
