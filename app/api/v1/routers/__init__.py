from .conversations_router import router as conversations_router
from .customers_router import router as customers_router
from .documents_router import router as documents_router
from .persons_router import router as persons_router

__all__ = ["customers_router", "conversations_router", "persons_router", "documents_router"]

