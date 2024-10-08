from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from handler.board import router as board_router
from handler.ideation import router as ideation_router
from handler.user import router as user_router
from handler.invest import router as invest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    await init_db()
    yield
    print("App is shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(board_router)
app.include_router(user_router)
app.include_router(ideation_router)
app.include_router(invest_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
