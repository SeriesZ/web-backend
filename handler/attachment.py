from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import enforcer, get_db
from model.attachment import Attachment, Comment
from model.user import User
from schema.attachment import (AttachmentResponse, CommentRequest,
                               CommentResponse)

router = APIRouter(tags=["코멘트"])


@router.get("/attachment/{id}", response_model=List[AttachmentResponse])
async def get_attachments(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    attachments = await db.execute(
        select(Attachment).where(Attachment.related_id == id)
    )
    attachments = attachments.scalars().all()
    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.get("/comment/{id}", response_model=List[CommentResponse])
async def get_comments(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    comments = await db.execute(
        select(Comment).where(Comment.related_id == id)
    )
    comments = comments.scalars().all()
    return [CommentResponse.model_validate(c) for c in comments]


@router.post("/comment")
async def create_comment(
    comment: CommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = Comment(
        **comment.dict(),
        user_id=current_user.id,
    )
    db.add(comment)
    await enforcer.add_policies(
        [
            (current_user.id, comment.id, "write"),
        ]
    )


@router.put("/comment/{id}", response_model=CommentResponse)
async def update_comment(
    id: str,
    request: CommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    comment = await db.execute(select(Comment).where(Comment.id == id))
    comment = comment.scalar_one()
    if not comment:
        raise HTTPException(status_code=404, detail="Ideation not found")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(comment, key, value)

    await db.refresh(comment)
    return CommentResponse.model_validate(comment)


@router.delete("/comment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    comment = await db.execute(delete(Comment).where(Comment.id == id))
    if not comment.scalar_one():
        raise HTTPException(status_code=404, detail="Ideation not found")
