from typing import Optional
import datetime
from pydantic import model_validator
from sqlmodel import Field, SQLModel
from database import engine

class User(SQLModel, table=True):
    __tablename__ = "Users"
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    user_name: Optional[str] = Field(default=None, unique=True, max_length=100)
    date_of_birth: str
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)
    updated_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow, sa_column_kwargs={"onupdate": datetime.datetime.utcnow})
    
    @model_validator(mode="before")
    def validate_names(cls, values):
        first_name = values.get("first_name")
        last_name = values.get("last_name")

        if first_name and not last_name:
            raise ValueError("If first_name is provided, last_name cannot be NULL")
        if last_name and not first_name:
            raise ValueError("If last_name is provided, first_name cannot be NULL")

        return values
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
