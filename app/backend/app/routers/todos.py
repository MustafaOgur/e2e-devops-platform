import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todos", tags=["todos"])


def get_todo_or_404(todo_id: int, db: Session = Depends(get_db)) -> Todo:
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(db: Session = Depends(get_db)):
    return db.scalars(select(Todo).order_by(Todo.id.desc())).all()


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(title=payload.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    logger.info("todo created: id=%s", todo.id)
    return todo


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo: Todo = Depends(get_todo_or_404)):
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    payload: TodoUpdate,
    todo: Todo = Depends(get_todo_or_404),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    logger.info("todo updated: id=%s", todo.id)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo: Todo = Depends(get_todo_or_404),
    db: Session = Depends(get_db),
) -> None:
    db.delete(todo)
    db.commit()
    logger.info("todo deleted: id=%s", todo.id)
