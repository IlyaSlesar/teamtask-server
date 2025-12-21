from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.session import init_db, engine
from api.routes import auth, project, task


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    if engine:
        await engine.dispose()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.router.lifespan_context = lifespan

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)
