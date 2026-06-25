import os
import jwt

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from services.user_service import (
    register_user,
    find_user_by_email,
    verify_password,
    find_user_by_id
)

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()

JWT_SECRET = os.getenv(
    "JWT_SECRET"
)


# REGISTER
@router.post("/register")
def register(
    name: str,
    email: str,
    password: str
):

    result = register_user(
        name,
        email,
        password
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return {
        "message": result["message"]
    }

@router.post("/login")
def login(
    email: str,
    password: str
):

    user = find_user_by_email(email)

    if user is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    # verify password
    if not verify_password(
        password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    # create jwt token
    token = jwt.encode(

        {
            "user_id": user["id"],
            "email": user["email"]
        },

        JWT_SECRET,

        algorithm="HS256"
    )

    return {

        "message":
        "Login successful",

        "token":
        token
    }


# DECODE TOKEN
def decode_token(
    token: str
):

    try:

        payload = jwt.decode(

            token,

            JWT_SECRET,

            algorithms=["HS256"]
        )

        return payload

    except jwt.InvalidTokenError:

        raise HTTPException(

            status_code=401,

            detail="Invalid or expired token"
        )


# GET CURRENT USER
def get_current_user(

    credentials:
    HTTPAuthorizationCredentials = Depends(security)

):

    token = credentials.credentials

    payload = decode_token(token)

    user = find_user_by_id(
        payload["user_id"]
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# AUTH ME
@router.get("/me")
def auth_me(

    current_user = Depends(
        get_current_user
    )

):

    return {

        "message":
        "User authenticated",

        "user": {

            "id":
            current_user["id"],

            "username":
            current_user["username"],

            "email":
            current_user["email"]
        }
    }