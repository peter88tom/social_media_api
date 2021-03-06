from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

"""
Three things we need to provide
1/ Secret_key
2/ Algorithm
3/ Exparation time
"""

# SECRET_KEY = "c39bb456133e99776f91e70886a605470451af0957d461bf801f86eea518da16"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Use environment variables
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
  to_encode = data.copy()

  expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})

  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return encoded_jwt

# Verify token
def verify_access_token(token: str, credentials_exception):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    id: str = payload.get("user_id")

    if id is None:
      raise credentials_exception
    token_data = schemas.TokenData(id=id)
  except JWTError:
    raise credentials_exception

  return token_data


"""
Get current user, this function will be injected as a dependency on
any of the end point where by it will get the passed token
, extract the id and bring for verification
"""
def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
  credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                        detail="Could not validate credentials",
                                        headers = {"WWW-Authenticate": "Bearer"})

  # Get  current user
  token = verify_access_token(token, credentials_exception)
  user = db.query(models.User).filter(models.User.id == token.id).first()
  return user
