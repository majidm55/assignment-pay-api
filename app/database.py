from dotenv import load_dotenv
from sqlmodel import Session, create_engine
import os

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
