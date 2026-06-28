from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskBatchUpdate
from app.utils.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["任务"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: int = Query(...),
    status: str = Query(None),
    priority: str = Query(None),
    assignee_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Task)
        .options(joinedload(Task.creator), joinedload(Task.assignee))
        .filter(Task.project_id == project_id)
    )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    return query.order_by(Task.sort_order, Task.created_at.desc()).all()


@router.post("", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    max_order = db.query(Task.sort_order).filter(Task.project_id == task_in.project_id).order_by(Task.sort_order.desc()).first()
    next_order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0

    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        project_id=task_in.project_id,
        creator_id=current_user.id,
        assignee_id=task_in.assignee_id,
        start_date=task_in.start_date,
        end_date=task_in.end_date,
        estimated_hours=task_in.estimated_hours,
        sort_order=next_order,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return db.query(Task).options(joinedload(Task.creator), joinedload(Task.assignee)).filter(Task.id == task.id).first()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).options(joinedload(Task.creator), joinedload(Task.assignee)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return db.query(Task).options(joinedload(Task.creator), joinedload(Task.assignee)).filter(Task.id == task.id).first()


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    db.delete(task)
    db.commit()
    return {"message": "任务已删除"}


@router.put("/{task_id}/status")
def update_task_status(
    task_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = status
    db.commit()
    return {"message": "状态已更新"}


@router.post("/batch-update")
def batch_update_tasks(
    batch: TaskBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = db.query(Task).filter(Task.id.in_(batch.task_ids)).all()
    for task in tasks:
        if batch.status:
            task.status = batch.status
        if batch.priority:
            task.priority = batch.priority
        if batch.assignee_id is not None:
            task.assignee_id = batch.assignee_id
    db.commit()
    return {"message": f"已更新 {len(tasks)} 个任务"}


@router.put("/reorder/{project_id}")
def reorder_tasks(
    project_id: int,
    task_orders: list[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for item in task_orders:
        task = db.query(Task).filter(Task.id == item["id"], Task.project_id == project_id).first()
        if task:
            task.sort_order = item["order"]
            if "status" in item:
                task.status = item["status"]
    db.commit()
    return {"message": "排序已更新"}
