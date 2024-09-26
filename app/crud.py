# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Todo operations
def get_todo(db: Session, todo_id: int, user_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()

def get_user_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_todo(db: Session, todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(**todo.dict(), owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()
    if db_todo:
        update_data = todo.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo

# Additional helper functions
def get_todos_by_category(db: Session, user_id: int, category: str, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id, models.Todo.category == category).offset(skip).limit(limit).all()

def get_todos_by_completion_status(db: Session, user_id: int, completed: bool, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id, models.Todo.completed == completed).offset(skip).limit(limit).all()

def get_todos_by_due_date(db: Session, user_id: int, start_date, end_date, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(
        models.Todo.owner_id == user_id,
        models.Todo.due_date >= start_date,
        models.Todo.due_date <= end_date
    ).offset(skip).limit(limit).all()