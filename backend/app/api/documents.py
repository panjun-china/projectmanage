import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/documents", tags=["文档"])

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".md", ".csv", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".zip", ".rar", ".7z",
}


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    project_id: int = Query(...),
    doc_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Document)
        .options(joinedload(Document.creator))
        .filter(Document.project_id == project_id)
    )
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    return query.order_by(Document.updated_at.desc()).all()


@router.post("", response_model=DocumentResponse)
def create_document(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = Document(
        title=doc_in.title,
        doc_type=doc_in.doc_type,
        content=doc_in.content,
        project_id=doc_in.project_id,
        creator_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return db.query(Document).options(joinedload(Document.creator)).filter(Document.id == doc.id).first()


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    project_id: int = Form(...),
    title: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_name

    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        title=title or file.filename,
        doc_type="file",
        file_path=str(file_path),
        file_name=file.filename,
        file_size=len(content),
        project_id=project_id,
        creator_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return db.query(Document).options(joinedload(Document.creator)).filter(Document.id == doc.id).first()


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).options(joinedload(Document.creator)).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int,
    doc_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    update_data = doc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)

    db.commit()
    db.refresh(doc)
    return db.query(Document).options(joinedload(Document.creator)).filter(Document.id == doc.id).first()


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "文档已删除"}


@router.get("/{doc_id}/download")
def download_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not doc.file_path:
        raise HTTPException(status_code=404, detail="文件不存在")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="文件已被删除")

    return FileResponse(doc.file_path, filename=doc.file_name)
