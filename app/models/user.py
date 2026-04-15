from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr

class SignBase(SQLModel,):
    user_id: int = Field(foreign_key="user.id")
    file_name: str
    description: str
    latitude: float
    longitude: float

class SignImage(SignBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="signs")

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""
    
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signs: list["SignImage"] = Relationship(back_populates="user")