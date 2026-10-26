from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    """
    Users table.
    Stores application user profiles synchronized from Firebase Authentication.
    Passwords are NOT stored here — Firebase handles all password and identity logic.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    file_references = db.relationship(
        "FileReference",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    upload_events = db.relationship(
        "UploadEvent",
        back_populates="user",
        lazy="dynamic",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}'>"
