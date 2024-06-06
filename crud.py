from sqlalchemy.orm import Session
from models import Appointment, Users
from schemas import AppointmentCreate, UserCreate, User
from passlib.context import CryptContext
from database import SessionLocal
import schemas
import redis,models
from kafka import KafkaProducer
from typing import List


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Inicijalizacija Kafka producenta
kafka_client = KafkaProducer(bootstrap_servers='up-kafka-1:9092')

# Funkcija za dohvaćanje svih zaposlenika iz baze podataka
def get_employees(db: Session):
    return db.query(models.Employees).all()

# Funkcija za dohvaćanje svih usluga iz baze podataka
def get_services(db: Session):
    return db.query(models.Services).all()

def hash_password(password: str):
    return pwd_context.hash(password)

def get_all_appointments(db: Session):
    return db.query(Appointment).all()

def get_appointment(db: Session, appointment_id: int):
    return db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()

def create_appointment(db: Session, appointment: AppointmentCreate):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment_data: AppointmentCreate):
    db_appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if db_appointment is None:
        return None
    for field, value in appointment_data.dict().items():
        setattr(db_appointment, field, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db.query(Appointment).filter(Appointment.appointment_id == appointment_id).delete()
    db.commit()

def get_user(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = Users(username=user.username, email=user.email, role=user.role, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

def register_user(db: Session, user: UserCreate) -> schemas.User:
    db_user = create_user(db, user)
    return schemas.User.from_orm(db_user)

def get_user_appointments(db: Session, user_id: int):
    return db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()

# Funkcija za dohvaćanje svih termina
def get_all_appointments(db: Session) -> List[Appointment]:
    return db.query(models.Appointment).all()

def get_employees(db: Session):
    return db.query(models.Employees).all()

def get_services(db: Session):
    return db.query(models.Services).all()

def get_all_appointments(db: Session) -> List[models.Appointment]:
    return db.query(models.Appointment).all()

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.appointment_id == appointment_id).first()

def init_db(db: Session):
    # Ovdje kreirajte sve tablice u bazi podataka
    models.Base.metadata.create_all(bind=db.get_bind())
    
    
