from typing import Union, Annotated
from fastapi import Depends, FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.templating import Jinja2Templates
from models import create_db_and_tables, User
from database import get_session
from sqlmodel import Field, Session, SQLModel, create_engine, select
import os

app = FastAPI()
SessionDep = Annotated[Session, Depends(get_session)]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("App started and DB connection checked.")

@app.get("/")
async def render_form(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("form.html", {"request": request, "users": users})


@app.get("/users/template/edit/{user_id}")
def edit_user(user_id: int, request: Request, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        return {"error": "User not found"}
    
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.post("/users/template")
async def create_user(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    user_name: str = Form(None),
    date_of_birth: str = Form(...),
    session: Session = Depends(get_session)
):
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
        date_of_birth=date_of_birth
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("form.html", {"request": request, "users": users})

@app.post("/users/template/update/{user_id}")
def update_user(
    user_id: int,
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    user_name: str = Form(None),
    date_of_birth: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        return {"error": "User not found"}
    
    user.first_name = first_name
    user.last_name = last_name
    user.user_name = user_name
    user.date_of_birth = date_of_birth

    session.add(user)
    session.commit()
    session.refresh(user)

    users = session.exec(select(User)).all()
    return templates.TemplateResponse("form.html", {"request": request, "users": users})

@app.post("/users/template/delete/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    hero = session.get(User, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(hero)
    session.commit()
    
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("form.html", {"request": {}, "users": users})

@app.get("/users/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Hero not found")
    return user

@app.post("/users/")
def create_user(
    user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    users = session.exec(select(User)).all()
    return users

@app.delete("/user/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    hero = session.get(User, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(hero)
    session.commit()
    
    users = session.exec(select(User)).all()
    return {"ok": True}