import os.path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Request
from sqlalchemy import and_
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse

from auth import get_current_user
from database import enforcer
from model.attachment import Attachment, Comment, Image
from model.user import User
from schema.attachment import (CommentRequest,
                               CommentResponse, AttachmentResponse)
from service.repository import CrudRepository, get_repository
from utils.path_util import save_file, save_image, get_file_path

router = APIRouter(tags=["코멘트"])


@router.get("/attachment/{id}")
async def download_attachment(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    # 데이터베이스에서 관련된 첨부 파일 찾기
    attachment = await repo.find_by_id(Attachment, id, field_name="id")

    file_path = get_file_path(attachment.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=attachment.file_name,
    )


@router.post("/attachment/{related_id}", response_model=AttachmentResponse)
async def upload_attachment(
        related_id: str,
        file: UploadFile = File(...),
        repo: CrudRepository = Depends(get_repository),
):
    attachment = await save_file(file, related_id)
    attachment = await repo.create(attachment)
    return attachment


@router.delete("/attachment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    await repo.delete(Attachment(id=id))


@router.post("/image/{related_id}", response_model=AttachmentResponse)
async def upload_image(
        request: Request,
        related_id: str,
        file: UploadFile = File(...),
        repo: CrudRepository = Depends(get_repository),
):
    image = await save_image(file, related_id, request)
    image = await repo.create(image)
    return image


@router.delete("/image/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    await repo.delete(Image(id=id))


@router.get("/comment/{id}", response_model=List[CommentResponse])
async def get_comments(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    comments = await repo.fetch_all(Comment, clauses=and_(Comment.related_id == id))
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
        id=id,
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
