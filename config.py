import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(BASE_DIR, "instance", "qrmedia.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    IMAGE_UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "images"
    )

    VIDEO_UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "videos"
    )

    QR_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "qr"
    )

    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    MAX_VIDEO_SIZE = 25 * 1024 * 1024
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4",
        "webm"
    }

    ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/webm"
}