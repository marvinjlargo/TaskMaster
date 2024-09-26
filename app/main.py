# app/main.py
from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import crud, models, schemas, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Welcome to the TaskMaster API"}

# User-related endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user

# Todo-related endpoints
@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return crud.create_user_todo(db=db, todo=todo, user_id=current_user.id)

@app.get("/todos/", response_model=List[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    todos = crud.get_user_todos(db, user_id=current_user.id, skip=skip, limit=limit)
    return todos

@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_todo = crud.get_todo(db, todo_id=todo_id, user_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_todo = crud.update_todo(db, todo_id=todo_id, todo=todo, user_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/todos/{todo_id}", response_model=schemas.Todo)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_todo = crud.delete_todo(db, todo_id=todo_id, user_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

# Additional endpoints for filtering and sorting
@app.get("/todos/category/{category}", response_model=List[schemas.Todo])
def read_todos_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    todos = crud.get_todos_by_category(db, user_id=current_user.id, category=category, skip=skip, limit=limit)
    return todos

@app.get("/todos/status/{completed}", response_model=List[schemas.Todo])
def read_todos_by_status(completed: bool, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    todos = crud.get_todos_by_completion_status(db, user_id=current_user.id, completed=completed, skip=skip, limit=limit)
    return todos

@app.get("/todos/due-date/", response_model=List[schemas.Todo])
def read_todos_by_due_date(
    start_date: str, 
    end_date: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    todos = crud.get_todos_by_due_date(
        db, 
        user_id=current_user.id, 
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )
    return todos