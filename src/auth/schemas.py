from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator


class UserBase(BaseModel):
    email: EmailStr
    password: str

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    password_2: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_2:
            raise ValueError('Passwords do not match')
        return self

class UserLoginSchema(UserBase): 
    pass

class UserReadSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    
    class Config: from_attributes = True