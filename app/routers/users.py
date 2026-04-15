from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, UploadFile, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import api_router, router
from app.services.user_service import UserService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.schemas import UserResponse
from app.models.user import SignImage
from app.image_utils import delete_sign_image, process_sign_image
from app.config import Settings
from typing import Annotated
from starlette.concurrency import run_in_threadpool
from PIL import UnidentifiedImageError
from . import templates



# API endpoint for listing users
@api_router.get("/users", response_model=list[UserResponse])
async def list_users(request: Request, db: SessionDep):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_all_users()

@api_router.post("/upload")
async def post_new_image(
    user: AuthDep,
    file: UploadFile,
    db: SessionDep,
    desc: Annotated[str, Form()],
    lat: Annotated[float, Form()],
    lng: Annotated[float, Form()]
):
    content = await file.read()

    if len(content) > (6 * 1024 * 1024):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is 6MB",
        )

    try:
        new_filename = await run_in_threadpool(process_sign_image, content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP).",
        ) from err

    try:
        db.add(SignImage(user_id=user.id, file_name=new_filename, description=desc, latitude=lat, longitude=lng))
        db.commit()
    except:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image upload failed",
        )

@router.get("/upload")
async def submit_view(
    user:AuthDep,
    request: Request, 
    db: SessionDep,
):
    user_images = db.exec(select(SignImage).where(SignImage.user_id == user.id)).all()
    user_images = list(user_images)
    return templates.TemplateResponse(
        request=request, 
        name="upload.html",
        context={
            "user": user,
            "user_images" : jsonable_encoder(user_images),
        }
    )

@api_router.get("/delete/{image_id}")
async def delete_user_image(
    user:AuthDep,
    request: Request, 
    db: SessionDep,
    image_id: int,
):
    url = "/upload"
    image = db.exec(select(SignImage).where(SignImage.id == image_id)).one_or_none()
    if not image:
        raise HTTPException(status_code = 404, detail="Image not found")
    if image.user_id != user.id:
        raise HTTPException(status_code= 401, detail="User does not own image")

    try:
        db.delete(image)
        delete_sign_image(image.file_name)
        db.commit()
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occured while attempting to delete the image")

