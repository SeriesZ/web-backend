import os.path
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from handler.attachment import router as attachment_router
from handler.board import router as board_router
from handler.ideation import router as ideation_router
from handler.invest import router as invest_router
from handler.user import router as user_router
from mock import create_mock


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    if os.path.exists("test.db"):
        await init_db()
    else:
        await init_db()
        await create_mock()
    yield
    print("App is shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(board_router)
app.include_router(user_router)
app.include_router(ideation_router)
app.include_router(invest_router)
app.include_router(attachment_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
