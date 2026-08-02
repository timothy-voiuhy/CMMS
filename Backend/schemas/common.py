from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    success: bool = True
    data: List[T]
    total: int
    page: int
    pageSize: int
    totalPages: int
