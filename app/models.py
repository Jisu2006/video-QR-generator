from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Video(db.Model):
    """
    Video entity storing metadata, unique URL references, and QR file paths.
    """
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, default=0, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False, default='video/mp4')
    video_url = db.Column(db.String(500), nullable=False)
    qr_code_path = db.Column(db.String(500), nullable=False)
    views_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def formatted_size(self):
        """Format bytes to human-readable size (KB, MB, GB)."""
        bytes_val = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    @property
    def formatted_date(self):
        """Format timestamp to friendly date string."""
        if not self.created_at:
            return ""
        return self.created_at.strftime('%b %d, %Y at %I:%M %p')

    @property
    def formatted_date_short(self):
        """Short date representation."""
        if not self.created_at:
            return ""
        return self.created_at.strftime('%Y-%m-%d')

    def to_dict(self):
        """Serialize video record to JSON-friendly dictionary."""
        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'title': self.title,
            'description': self.description,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'formatted_size': self.formatted_size,
            'mime_type': self.mime_type,
            'video_url': self.video_url,
            'qr_code_path': self.qr_code_path,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'formatted_date': self.formatted_date
        }


class Admin(db.Model):
    """
    Admin user model for dashboard authentication.
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class AppSetting(db.Model):
    """
    Dynamic application settings table.
    """
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=None):
        record = cls.query.filter_by(setting_key=key).first()
        return record.setting_value if record else default

    @classmethod
    def set(cls, key, value):
        record = cls.query.filter_by(setting_key=key).first()
        if record:
            record.setting_value = value
        else:
            record = cls(setting_key=key, setting_value=value)
            db.session.add(record)
        db.session.commit()
