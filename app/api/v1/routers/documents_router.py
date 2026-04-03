from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from app.api.dependencies import (
    get_delete_document_uc,
    get_get_document_uc,
    get_list_documents_uc,
    get_upload_document_uc,
)
from app.api.v1.schemas import DocumentContentResponse, DocumentResponse
from app.domain.errors import DocumentNotFoundError, PersonNotFoundError
from app.use_cases.documents import (
    DeleteDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    UploadDocumentUseCase,
)


router = APIRouter(tags=["documents"])

ALLOWED_EXTENSIONS = {".txt", ".md"}


@router.post(
    "/persons/{person_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    person_id: UUID,
    file: UploadFile = File(...),
    use_case: UploadDocumentUseCase = Depends(get_upload_document_uc),
) -> DocumentResponse:
    """Загрузить документ к карточке (.txt или .md)."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя файла отсутствует",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Разрешены только файлы {ALLOWED_EXTENSIONS}",
        )

    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть в кодировке UTF-8",
        ) from exc

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не может быть пустым",
        )

    try:
        document = await use_case.execute(
            person_id=str(person_id),
            filename=file.filename,
            content=content,
        )
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return DocumentResponse.model_validate(document)


@router.get("/persons/{person_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    person_id: UUID,
    use_case: ListDocumentsUseCase = Depends(get_list_documents_uc),
) -> list[DocumentResponse]:
    """Получить список документов карточки."""
    try:
        documents = await use_case.execute(person_id)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/documents/{document_id}", response_model=DocumentContentResponse)
async def get_document(
    document_id: UUID,
    use_case: GetDocumentUseCase = Depends(get_get_document_uc),
) -> DocumentContentResponse:
    """Получить документ с содержимым."""
    try:
        document = await use_case.execute(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден",
        ) from exc

    return DocumentContentResponse.model_validate(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    use_case: DeleteDocumentUseCase = Depends(get_delete_document_uc),
) -> Response:
    """Удалить документ."""
    try:
        await use_case.execute(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
