from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel

class Users(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'korisnik', 'zaposlenik'), nullable=False)

    appointments = relationship("Appointment", back_populates="user")

class Employees(Base):
    __tablename__ = 'Employees'

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)

    appointments = relationship("Appointment", back_populates="employee")

class Services(Base):
    __tablename__ = 'Services'

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    price = Column(DECIMAL(10, 2), nullable=False)

    appointments = relationship("Appointment", back_populates="service")

class Appointment(Base):
    __tablename__ = 'Appointments'

    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    employee_id = Column(Integer, ForeignKey('Employees.employee_id'))
    service_id = Column(Integer, ForeignKey('Services.service_id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    user = relationship("Users", back_populates="appointments")
    employee = relationship("Employees", back_populates="appointments")
    service = relationship("Services", back_populates="appointments")

class Clients(Base):
    __tablename__ = 'Clients'

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone_number = Column(String(20))

class UserBase(BaseModel):
    username: str
    email: str
    password: str
    role: str
    
class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True
    