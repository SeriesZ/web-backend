import os.path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from database import init_db
from handler.attachment import router as attachment_router
from handler.board import router as board_router
from handler.chat import router as chat_router
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
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (보안 문제를 피하려면 필요한 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
