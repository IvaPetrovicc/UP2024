from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import crud, database, security, models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "5f24276349b533fd412dc5ddf17280dde3bdfc2d43e426815f778c73e9541322"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to decode access token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Function to get current user based on token from header or cookie
def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Check for token in the request header or cookies
    if not token:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception

    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Function to get database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    response = RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="user_id", value=user.user_id)  # Set the user_id in the cookies
    return response


@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    username = request.cookies.get("username")
    if username:
        return templates.TemplateResponse("index.html", {"request": request, "username": username})
    else:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    user = schemas.UserCreate(username=username, email=email, password=password, role=role)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    crud.register_user(db=db, user=user)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint to create an appointment
@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_appointment(db=db, appointment=appointment)

@app.get("/appointments/user", response_model=List[schemas.Appointment])
def read_user_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    appointments = crud.get_user_appointments(db, current_user.user_id)
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for this user")
    return appointments

# Protected endpoint to read a specific appointment
@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_appointment = crud.get_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

# Protected endpoint to read all appointments
@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_all_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_all_appointments(db)

# Protected endpoint to update an appointment
@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int,
    appointment_data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_appointment = crud.get_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return crud.update_appointment(db, appointment_id, appointment_data)

# Protected endpoint to delete an appointment
@app.delete("/appointments/{appointment_id}", response_model=schemas.Appointment)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_appointment = crud.get_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    crud.delete_appointment(db, appointment_id)
    return db_appointment

@app.get("/moji-termini", response_class=HTMLResponse)
async def moji_termini(request: Request):
    return templates.TemplateResponse("moji-termini.html", {"request": request})

@app.get("/logout")
async def logout_get(request: Request, response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("username")
    response.delete_cookie("access_token")
    return response

@app.get("/edit-appointment/{appointment_id}", response_class=HTMLResponse)
async def edit_appointment(request: Request, appointment_id: int):
    return templates.TemplateResponse("edit-appointment.html", {"request": request, "appointment_id": appointment_id})


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    crud.init_db(db)
