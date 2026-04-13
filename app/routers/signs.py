from fastapi.responses import RedirectResponse
from fastapi import Request, status
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.models.user import SignImage
from app.schemas.user import SignPublic
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
import json
from . import api_router

@api_router.get("/signs")
async def get_signs(
    user: AuthDep,
    request: Request, 
    db: SessionDep,
): 
    statement = select(SignImage).options(selectinload(SignImage.user))
    db_signs = db.exec(statement).all()

    signs = [SignPublic.model_validate(s) for s in db_signs]

    return json.dumps(signs)