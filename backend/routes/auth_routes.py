from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from database.db import get_db_connection, execute_query, commit_changes, close_connection
from security import hash_password, verify_password, create_token

router = APIRouter()


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =========================
# REGISTER
# =========================

@router.post("/register")
def register(user: UserRegister):

    conn = get_db_connection()

    try:
        existing = execute_query(
            conn,
            "SELECT id FROM users WHERE email=%s",
            (user.email,),
            fetchone=True
        )

        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(user.password)

        execute_query(
            conn,
            "INSERT INTO users(username,email,password_hash) VALUES(%s,%s,%s)",
            (user.username, user.email, hashed)
        )

        commit_changes(conn)

        return {"message": "User created"}

    finally:
        close_connection(conn)


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(user: UserLogin):

    conn = get_db_connection()

    try:
        db_user = execute_query(
            conn,
            "SELECT * FROM users WHERE email=%s",
            (user.email,),
            fetchone=True
        )

        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token({"user_id": db_user["id"]})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        close_connection(conn)