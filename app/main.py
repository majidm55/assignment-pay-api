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
    users = session.exec(select(User)).all()  # Fetch all users
    return templates.TemplateResponse("form.html", {"request": request, "users": users})



@app.get("/users/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.post("/users/")
def create_user(
    user: User, session: SessionDep, request: Request) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("form.html", {"request": request, "users": users})
