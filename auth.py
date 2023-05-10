from fastapi import FastAPI as fp, Depends, status, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel 
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
#######################################
##### Secrets and constants ###########
my_secret_key = os.environ.get('SECRET_KEY') # stored in a .env file that is not uploaded to git
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRY_MINUTES = 30
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
#######################################
### Pwd context and oauthScheme Depd ##
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
#######################################
##### Fake Db #########################
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


####### Pydantic Models defn ###########
class Token(BaseModel):
    access_token: int
    token_type: str = 'bearer'

class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str|None = None
    full_name: str|None = None
    disabled: bool|None = None

class UserInDB(User):
    hashed_password: str

##### User Util #################################
def get_user(db: dict, username: str) -> UserInDB:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

########## Password Hash Utils ###################

def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_password_hash(plain_pwd: str):
    return pwd_context.hash(plain_pwd)

fake_users_db['alice']["hashed_password"] = get_password_hash("secret")
fake_users_db['johndoe']["hashed_password"] = get_password_hash("secret")

def authenticate_user(username: str, password: str) -> UserInDB | bool:
    user = get_user(fake_users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

############# Create JWT token util
def create_access_token(data: dict, expires_delta: timedelta = ACCESS_TOKEN_EXPIRY_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, my_secret_key, algorithm=ALGORITHM)
    return jwt_token




    
def decode_token(token: str) -> UserInDB:
    try:
        payload = jwt.decode(token, my_secret_key, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return get_user(fake_users_db, token_data.username)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_token(token=token)
    if not user:
        raise credentials_exception
    return user

async def get_current_active_user(user: Annotated[UserInDB, Depends(get_current_user)]):
    if not user.disabled:
        return user
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

################ APP routes start here ############################################
app = fp()

@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_in_db = authenticate_user(form_data.username, form_data.password)
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect Username or Passowrd",
                            headers={"WWW-Authenticate": "Bearer"})
    print("Authenticated", user_in_db)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    access_token = create_access_token(data={'sub':  user_in_db.username},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/users/me', response_model=User)
def read_user(user: Annotated[User, Depends(get_current_active_user)]):
    return user

@app.get("/whatIsMyToken")
def read_token(token: Annotated[str, Depends(oauth2_scheme)]):
    return {'token': token}