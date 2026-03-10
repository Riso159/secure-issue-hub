import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, csrf_protect
from app.db.database import get_db
from app.core.security import hash_password, verify_password
from app.schemas.auth import RegisterRequest, LoginRequest, UserPublic
from app.services.users import get_user_by_email, create_user
from app.services.sessions import create_session, get_session, revoke_session


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(resp: Response, sid: str, csrf: str) -> None:
    resp.set_cookie(
        key=settings.session_cookie_name,
        value=sid,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    resp.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def _clear_auth_cookies(resp: Response) -> None:
    resp.delete_cookie(settings.session_cookie_name, path="/")
    resp.delete_cookie(settings.csrf_cookie_name, path="/")


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = create_user(db, payload.email, hash_password(payload.password))
    return UserPublic(id=user.id, email=user.email)


@router.post("/login", response_model=UserPublic)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    sess = create_session(db, user.id)
    _set_auth_cookies(response, str(sess.id), sess.csrf_token)

    return UserPublic(id=user.id, email=user.email)


@router.get("/me", response_model=UserPublic)
def me(user=Depends(get_current_user)):
    return UserPublic(id=user.id, email=user.email)


@router.get("/csrf")
def csrf(request: Request):
    # frontend si to vie zobrať aj z cookie, ale toto je pohodlnejšie na testovanie
    token = request.cookies.get(settings.csrf_cookie_name)
    return {"csrf": token}


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf=Depends(csrf_protect),
):
    sid = request.cookies.get(settings.session_cookie_name)
    if sid:
        try:
            sid_uuid = uuid.UUID(sid)
            sess = get_session(db, sid_uuid)
            if sess:
                revoke_session(db, sess)
        except ValueError:
            pass

    _clear_auth_cookies(response)
    return {"ok": True}
