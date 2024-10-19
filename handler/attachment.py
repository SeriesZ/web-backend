from typing import List

from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer
from model.attachment import Attachment, Comment
from model.user import User
from schema.attachment import (AttachmentResponse, CommentRequest,
                               CommentResponse)
from service.repository import get_repository, CrudRepository

router = APIRouter(tags=["코멘트"])


@router.get("/attachment/{id}", response_model=List[AttachmentResponse])
async def get_attachments(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    attachments = await repo.find_by_id(Attachment, id, field_name="related_id")
    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.get("/comment/{id}", response_model=List[CommentResponse])
async def get_comments(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    comments = await repo.find_by_id(Comment, id, field_name="related_id")
    return [CommentResponse.model_validate(c) for c in comments]


@router.post("/comment", response_model=CommentResponse)
async def create_comment(
        comment: CommentRequest,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    comment = Comment(
        **comment.dict(),
        user_id=current_user.id,
    )
    comment = await repo.create(comment)
    await enforcer.add_policies(
        [
            (current_user.id, comment.id, "write"),
        ]
    )
    return CommentResponse.model_validate(comment)


@router.put("/comment/{id}", response_model=CommentResponse)
async def update_comment(
        id: str,
        request: CommentRequest,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    comment = Comment(
        **request.dict(),
        user_id=current_user.id,
    )
    comment = await repo.update(comment)
    return CommentResponse.model_validate(comment)


@router.delete("/comment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        id: str,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")
    await repo.delete(Comment(id=id))
