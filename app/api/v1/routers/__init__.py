from .chat_router import router as chat_router
from .documents_router import router as documents_router
from .filters_router import router as filters_router
from .persons_router import router as persons_router

__all__ = [
    "persons_router",
    "documents_router",
    "chat_router",
    "filters_router",
]
