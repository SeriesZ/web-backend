import os
from uuid import uuid4

from fastapi import Request

from common.config import ASSETS_DIR, DOWNLOAD_DIR
from model.attachment import Attachment, Image


def get_url(request: Request, file_path) -> str:
    return f"{request.url.scheme}://{request.url.netloc}/assets/{file_path}"


async def save_image(image, related_id: str, request: Request) -> Image:
    image_filename = f"{uuid4()}_{image.filename}"
    image_path = os.path.join(ASSETS_DIR, image_filename)
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())
    return Image(
        related_id=related_id,
        file_name=image.filename,
        file_path=get_url(request, image_filename),
    )


async def save_file(file, related_id: str) -> Attachment:
    file_name = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return Attachment(
        related_id=related_id,
        file_name=file.filename,
        file_path=file_name
    )


def get_file_path(file_name):
    return os.path.join(DOWNLOAD_DIR, file_name)
