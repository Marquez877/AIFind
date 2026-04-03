from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import (
    get_create_customer_uc,
    get_delete_customer_uc,
    get_get_customer_uc,
    get_list_customers_uc,
    get_update_customer_uc,
)
from app.api.v1.schemas import CustomerCreateRequest, CustomerResponse, CustomerUpdateRequest
from app.domain.errors import CustomerAlreadyExistsError, CustomerNotFoundError
from app.use_cases.customers import (
    CreateCustomerUseCase,
    DeleteCustomerUseCase,
    GetCustomerUseCase,
    ListCustomersUseCase,
    UpdateCustomerUseCase,
)


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreateRequest,
    use_case: CreateCustomerUseCase = Depends(get_create_customer_uc),
) -> CustomerResponse:
    try:
        customer = await use_case.execute(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            company=payload.company,
        )
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CustomerResponse.model_validate(customer)


@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    company: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    use_case: ListCustomersUseCase = Depends(get_list_customers_uc),
) -> list[CustomerResponse]:
    customers = await use_case.execute(name, email, company, is_active, limit, offset)
    return [CustomerResponse.model_validate(customer) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    use_case: GetCustomerUseCase = Depends(get_get_customer_uc),
) -> CustomerResponse:
    try:
        customer = await use_case.execute(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found") from exc

    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    payload: CustomerUpdateRequest,
    use_case: UpdateCustomerUseCase = Depends(get_update_customer_uc),
) -> CustomerResponse:
    updates = payload.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="name cannot be null")
    if "email" in updates and updates["email"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email cannot be null")

    try:
        customer = await use_case.execute(customer_id, **updates)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found") from exc
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    use_case: DeleteCustomerUseCase = Depends(get_delete_customer_uc),
) -> Response:
    try:
        await use_case.execute(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found") from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
