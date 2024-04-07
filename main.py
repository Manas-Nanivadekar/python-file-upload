from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from fastapi.responses import StreamingResponse
import io

DATABASE_URL = "postgresql://admin:password@localhost/fileupload"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    content = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

# Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# API Endpoints
@app.post("/signup/")
def create_user_signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return {"username": user.username, "message": "User created successfully."}

@app.post("/uploadfile")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_content = file.file.read()
    db_file = FileRecord(filename=file.filename, content=file_content)
    db.add(db_file)
    db.commit()
    return {"filename": file.filename, "message": "File uploaded successfully."}

@app.get("/files/", response_model=List[str])
def read_files(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = db.query(FileRecord.filename).all()
    return [file.filename for file in files]


@app.get("/files/download/{filename}")
async def download_file(filename: str, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.filename == filename).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(io.BytesIO(file_record.content), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})