from datetime import datetime, timezone
from app.extensions import db


class StoredFile(db.Model):
    """
    StoredFiles table.
    Represents unique physical file content deduplicated by SHA-256 hash.
    One row represents exactly one physical file stored in Firebase Cloud Storage.
    """
    __tablename__ = "stored_files"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sha256_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    file_size = db.Column(db.BigInteger, nullable=False)  # stored in bytes
    storage_path = db.Column(db.String(512), nullable=False)  # e.g., objects/<sha256_hash>
    mime_type = db.Column(db.String(128), default="application/octet-stream", nullable=False)
    reference_count = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    file_references = db.relationship(
        "FileReference",
        back_populates="stored_file",
        lazy="dynamic",
    )
    upload_events = db.relationship(
        "UploadEvent",
        back_populates="stored_file",
        lazy="dynamic",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sha256_hash": self.sha256_hash,
            "file_size": self.file_size,
            "storage_path": self.storage_path,
            "mime_type": self.mime_type,
            "reference_count": self.reference_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<StoredFile id={self.id} hash='{self.sha256_hash[:10]}...' size={self.file_size} refs={self.reference_count}>"
