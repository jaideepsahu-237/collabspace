from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name : str = Field(min_length=2, max_length=100)
    email : EmailStr
    password : str = Field(min_length=2, max_length=128)
    tenant_id : int = Field(gt=0)

class UserResponse(BaseModel):
    id : int
    name : str
    email : EmailStr
    tenant_id : int

    model_config = ConfigDict(from_attributes=True)