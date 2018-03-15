from datetime import datetime

from .. import db


class BaseModel(db.Model):
    __abstract__ = True  # Tells SQLAlchemy not to make a table for this class
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
