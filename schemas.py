from pydantic import BaseModel, EmailStr
from datetime import datetime


class AppointmentBase(BaseModel):
    user_id: int
    employee_id: int
    service_id: int
    start_time: datetime
    end_time: datetime


class AppointmentCreate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    appointment_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int = None
    password: str

    class Config:
        orm_mode = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserLogin(BaseModel):
    username: str
    password: str

class EmployeeBase(BaseModel):
    employee_name: str
    position: str

    class Config:
        orm_mode = True

class EmployeeCreate(EmployeeBase):
    pass

class Employees(EmployeeBase):
    employee_id: int

    class Config:
        orm_mode = True

class ServiceBase(BaseModel):
    service_name: str
    duration: int
    price: float

    class Config:
        orm_mode = True

class ServiceCreate(ServiceBase):
    pass

class Services(ServiceBase):
    service_id: int

    class Config:
        orm_mode = True