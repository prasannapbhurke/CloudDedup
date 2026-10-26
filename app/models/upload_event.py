from datetime import datetime, timezone
from app.extensions import db


class UploadEvent(db.Model):
    """
    UploadEvents table.
    Tracks historical upload activity and deduplication decisions over time.
    Remains intact even if a file reference is later deleted, ensuring accurate audit and trend metrics.
    """
    __tablename__ = "upload_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stored_file_id = db.Column(
        db.Integer, db.ForeignKey("stored_files.id", ondelete="SET NULL"), nullable=True, index=True
    )
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)  # size in bytes
    sha256_hash = db.Column(db.String(64), nullable=False, index=True)
    event_type = db.Column(db.String(32), nullable=False)  # 'new_upload' or 'duplicate_detected'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = db.relationship("User", back_populates="upload_events")
    stored_file = db.relationship("StoredFile", back_populates="upload_events")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stored_file_id": self.stored_file_id,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "sha256_hash": self.sha256_hash,
            "short_hash": self.sha256_hash[:12] if self.sha256_hash else "",
            "event_type": self.event_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<UploadEvent id={self.id} user_id={self.user_id} file='{self.original_filename}' type='{self.event_type}'>"
