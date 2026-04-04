from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import (
	chat_router,
	conversations_router,
	documents_router,
	filters_router,
	persons_router,
)
from app.api.v1.routers.auth_router import router as auth_router
from app.api.v1.routers.moderation_router import router as moderation_router
from app.api.v1.routers.person_conversations_router import router as person_conversations_router


app = FastAPI(title="Голос из архива — Backend")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(persons_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(filters_router, prefix="/api/v1")
app.include_router(moderation_router, prefix="/api/v1")
app.include_router(person_conversations_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
