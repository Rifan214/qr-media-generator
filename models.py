from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Media(db.Model):

    __tablename__ = "media"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    media_type = db.Column(
        db.String(20),
        nullable=False
    )

    file_extension = db.Column(
        db.String(20),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    qr_filename = db.Column(
        db.String(255),
        nullable=False
    )

    public_token = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    scan_count = db.Column(
        db.Integer,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "media_type": self.media_type,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "qr_filename": self.qr_filename,
            "public_token": self.public_token,
            "scan_count": self.scan_count,
            "created_at": self.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }