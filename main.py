import logging as logs

from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import Body, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database_client import DatabaseClient
from app.models.user import User
from app.schemas.user import AuthToken, UserRecord
from app.schemas.user_form import UserCreate, UserLogin

# Logger Setup
logs.basicConfig(level=logs.INFO)
logger = logs.getLogger(__name__)

# Startup Config
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Tables")
    client = DatabaseClient()
    client.model_base.metadata.create_all(bind=client.engine)
    logger.info("Initialization Successful")
    yield

app = FastAPI(
    title="Calculations API",
    description="API for managing calculations",
    version="1.0.0",
    lifespan=lifespan
)

# ----------------------------------------
# Health Endpoint
# ----------------------------------------
@app.get("/health", tags["health"])
def read_health():
    return {"status": "ok"}

# ----------------------------------------
# User Registration Endpoint
# ----------------------------------------
@app.post(
    "/auth/register",
    response_model=UserRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"]
)
def register(
        user_create: UserCreate,
        db: Session = Depends(DatabaseClient().get_session)):
    user_data = user_create.dict(exclude={"confirm_password"})
    try:
        user = User.register(db, user_data)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ----------------------------------------
# User Login Endpoints
# ----------------------------------------
@app.post("/auth/login", response_model=AuthToken, tags=["auth"])
def login_json(
        user_login: UserLogin,
        db: Session = Depends(DatabaseClient().get_session)):
    """Login with JSON data, ex. from a login screen"""
    auth_result = User.authenticate(db, user_login.username, user_login.password)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db.commit()
    return auth_result

@app.post("/auth/token", tags=["auth"])
def login_form(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(DatabaseClient().get_session)):
    """Login with form data, ex. from Swagger UI"""
    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }

# ----------------------------------------
# Calculation Endpoints
# ----------------------------------------


# ----------------------------------------
# Launch Script
# ----------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
