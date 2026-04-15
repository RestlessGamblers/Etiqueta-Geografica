from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import Request, status, Form, HTTPException
from app.dependencies import SessionDep
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from . import router, templates

# View route (loads the page)
@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="register.html",
    )

# Action route (performs an action)
@router.post('/register')
def signup_user(db: SessionDep, 
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        user = auth_service.register_user(username, email, password)
        # Return JSON instead of a Redirect
        return JSONResponse(content={"message": "Success"}, status_code=201)
    except Exception as e:
        # Return a 400 error with JSON detail
        return JSONResponse(content={"detail": "Username or email already exists"}, status_code=400)