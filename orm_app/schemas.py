from pydantic import  BaseModel, EmailStr
from datetime import  datetime

# Define base model
class PostBase(BaseModel):
  title: str
  content: str
  published: bool = True


# Extend base model
class CreatePost(PostBase):
  pass


# Define what field to return on response
class Post(PostBase):
  id: int
  created_at: datetime

  """
  Add class Config to tell pydantic model to read the data
  even if it is not dictionary but an orm model or any other
  arbitrary object with attributes
  """
  class Config:
    orm_mode= True


# Create user
class CreateUser(BaseModel):
  email :EmailStr
  password: str


# Define what to return after user created
class CreateUserResponse(BaseModel):
  id: int
  email : EmailStr
  created_at: datetime

  class Config:
    orm_mode= True
