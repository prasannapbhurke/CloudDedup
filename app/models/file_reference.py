from datetime import datetime, timezone
from app.extensions import db


class FileReference(db.Model):
    """
    FileReferences table.
    Represents logical file instances as perceived by the logged-in user.
    Each user has their own isolated references.
    Multiple references can point to the same StoredFile (content deduplication).
    No unique constraint on display_name or user_id + stored_file_id.
    """
    __tablename__ = "file_references"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stored_file_id = db.Column(
        db.Integer, db.ForeignKey("stored_files.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    display_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    is_duplicate = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="file_references")
    stored_file = db.relationship("StoredFile", back_populates="file_references")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stored_file_id": self.stored_file_id,
            "display_name": self.display_name,
            "file_size": self.stored_file.file_size if self.stored_file else 0,
            "sha256_hash": self.stored_file.sha256_hash if self.stored_file else "",
            "short_hash": self.stored_file.sha256_hash[:12] if self.stored_file else "",
            "mime_type": self.stored_file.mime_type if self.stored_file else "application/octet-stream",
            "is_duplicate": self.is_duplicate,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }

    def __repr__(self):
        return f"<FileReference id={self.id} user_id={self.user_id} name='{self.display_name}' dup={self.is_duplicate}>"
