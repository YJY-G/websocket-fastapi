from fastapi import Depends,HTTPException,Path, APIRouter,Request,Form
from pydantic import BaseModel,Field,EmailStr
from starlette import status
from models import User
from passlib.context import CryptContext
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta,timezone
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

SECRET_KEY = "449bb7ed4e376b1de2afc81695ebc3759b22bff8974dda503db5096dd3a88277"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

db_dependency = Depends(get_db)

class UserRequest(BaseModel):
    username: str = Field(...,title="用户名",max_length=20)
    password: str = Field(...,title="密码",max_length=20,min_length=6)
    user_type: str = Field("user",title="用户类型")

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(request: Request,username:str = Form(...),password:str=Form(...),db: Session = db_dependency):
    user = User(username=username,password=bcrypt_context.hash(password),user_type="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse("login.html", {"request": request})


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.password):
        return False
    return user

def create_access_token(username:str,user_id:int, expires_delta: timedelta = None):
    to_encode = {"sub": username, "user_id": user_id,"exp": datetime.now(timezone.utc) + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=Token)  
async def login_for_access_token(  
    form_data: OAuth2PasswordRequestForm = Depends(),  
    db: Session = db_dependency  
):  
    user = authenticate_user(db, form_data.username, form_data.password)  
    if not user:  
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="不正确的用户名或密码")  
    
    access_token_expires = timedelta(minutes=30)  
    access_token = create_access_token(  
        username=user.username,  
        user_id=user.id,  
        expires_delta=access_token_expires  
    )  
    
    return {  
        "access_token": access_token,  
        "token_type": "bearer"  
    }

@router.get("/register")  
async def get_register_form(request: Request):  
    return templates.TemplateResponse("register.html", {"request": request})  

@router.get("/login")  
async def get_login_form(request: Request):  
    return templates.TemplateResponse("login.html", {"request": request}) 