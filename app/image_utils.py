import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

SIGN_PICS_DIR = Path("app/media/sign_pics")

#Handle image processing based on the bytes collected from the user
def process_sign_image(content: bytes) -> str:
    with Image.open(BytesIO(content)) as original:
        #Automatically rotate the image based on its exif tag
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (500, 500), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.covert("RGB")
        
        #Generate a random file name
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = SIGN_PICS_DIR / filename

        #If the directory does not exist then create it and if it does exist do not throw an error
        SIGN_PICS_DIR.mkdir(parents=True, exist_ok=True)

        img.save(filepath, "JPEG", quality=85, optimize=True)

    return filename

#Delete a picture from the directory based on its filename
def delete_sign_image(filename: str | None) -> None:
    if filename is None:
        return
    
    filepath = SIGN_PICS_DIR / filename
    if filepath.exists():
        filepath.unlink()