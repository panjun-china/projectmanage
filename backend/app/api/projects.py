from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.project import Project, project_members
from app.models.task import Task
from app.models.document import Document
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/projects", tags=["项目"])


@router.get("", response_model=list[ProjectListResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = (
        db.query(Project)
        .options(joinedload(Project.owner))
        .filter(
            (Project.owner_id == current_user.id)
            | Project.members.any(User.id == current_user.id)
        )
        .all()
    )
    return projects


@router.post("", response_model=ProjectResponse)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        start_date=project_in.start_date,
        end_date=project_in.end_date,
        owner_id=current_user.id,
    )
    project.members.append(current_user)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _build_project_response(project, db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).options(joinedload(Project.owner)).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return _build_project_response(project, db)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return _build_project_response(project, db)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有项目创建者可以删除项目")

    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}


@router.post("/{project_id}/members/{user_id}")
def add_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user in project.members:
        raise HTTPException(status_code=400, detail="用户已是项目成员")

    project.members.append(user)
    db.commit()
    return {"message": "成员已添加"}


@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user not in project.members:
        raise HTTPException(status_code=404, detail="成员不存在")

    if user.id == project.owner_id:
        raise HTTPException(status_code=400, detail="不能移除项目创建者")

    project.members.remove(user)
    db.commit()
    return {"message": "成员已移除"}


@router.get("/{project_id}/members")
def get_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    from app.schemas.user import UserResponse
    return [UserResponse.model_validate(m) for m in project.members]


def _build_project_response(project: Project, db: Session) -> ProjectResponse:
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    done_count = db.query(Task).filter(Task.project_id == project.id, Task.status == "done").count()
    doc_count = db.query(Document).filter(Document.project_id == project.id).count()
    member_count = len(project.members)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        owner_id=project.owner_id,
        owner=project.owner,
        created_at=project.created_at,
        updated_at=project.updated_at,
        task_count=task_count,
        done_count=done_count,
        member_count=member_count,
        doc_count=doc_count,
    )
