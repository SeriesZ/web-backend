from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from handler.board import router as board_router
from handler.user import router as user_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    await init_db()
    yield
    print("App is shutting down...")


app.include_router(board_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
