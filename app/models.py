import sqlalchemy_utils as sau

from datetime import datetime

from . import db


class BaseModel(db.Model):
    __abstract__ = True  # Tells SQLAlchemy not to make a table for this class
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)


author_addon_table = db.Table('author_addon', db.Model.metadata,
                              db.Column('author', db.String, db.ForeignKey('author.name')),
                              db.Column('addon', db.Integer, db.ForeignKey('addon.addon_id')))


class AuthorModel(BaseModel):
    __tablename__ = 'author'
    name = db.Column(db.String, primary_key=True)

    primary_addons = db.relationship('AddonModel', backref='primary_author', lazy='dynamic')
    addons = db.relationship('AddonModel', secondary=author_addon_table, backref='authors', lazy='dynamic')

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @classmethod
    def update(cls, data: dict):
        obj = cls.query.get(data['Name'])
        if obj is None:
            obj = cls(data['Name'])
        db.session.add(obj)
        db.session.commit()
        return obj


class FileModel(BaseModel):
    __tablename__ = 'file'
    file_id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    name = db.Column(db.String, nullable=True)
    # The API doesn't think alts exists, so meh
    # alt_id = db.Column(db.Integer, db.ForeignKey(id), primary_key=True)

    url = db.Column(sau.URLType, nullable=True)
    # alt = db.relationship('file', backref='primary', lazy='dynamic')

    def __init__(self, id_: int, addon_id: int):
        super().__init__()
        self.file_id = id_
        self.addon_id = addon_id

        if AddonModel.query.get(addon_id) is None:
            db.session.add(AddonModel(addon_id))
            # generates excessive load, periodic cleanup is better
            # tasks.fill_missing_addon.delay(addon_id)
            db.session.commit()

    @classmethod
    def update(cls, addon_id: int, data: dict):
        obj = cls.query.get((data['Id'], addon_id))
        if obj is None:
            obj = cls(data['Id'], addon_id)

        obj.name = data['FileNameOnDisk']
        obj.url = data['DownloadURL']

        db.session.add(obj)
        db.session.commit()
        return obj


class AddonModel(BaseModel):
    __tablename__ = 'addon'
    addon_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String, nullable=True)
    category = db.Column(db.String, nullable=True)
    downloads = db.Column(db.BigInteger, nullable=True)
    score = db.Column(db.Float, nullable=True)

    primary_author_name = db.Column(db.String, db.ForeignKey(AuthorModel.name, onupdate='cascade', ondelete='cascade'), nullable=True)

    files = db.relationship('FileModel', backref='addon', lazy='dynamic')

    def __init__(self, id_: int):
        super().__init__()
        self.addon_id = id_

    @classmethod
    def update(cls, data: dict):
        obj = cls.query.get(data['Id'])
        if obj is None:
            obj = cls(data['Id'])

        for author in data['Authors']:
            obj.authors.append(AuthorModel.update(author))

        obj.name = data['Name']
        obj.game_id = data['GameId']
        obj.primary_author_name = data['PrimaryAuthorName']
        obj.category = data['CategorySection']['Name']
        obj.downloads = data['DownloadCount']
        obj.score = data['PopularityScore']

        db.session.add(obj)
        db.session.commit()

        if data['LatestFiles'] is not None:
            for file in data['LatestFiles']:
                FileModel.update(data['Id'], file)

        return obj


class HistoricRecord(db.Model):
    __tablename__ = 'history'
    timestamp = db.Column(db.DateTime, nullable=False, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    downloads = db.Column(db.BigInteger)
    score = db.Column(db.Float)

    def __init__(self, timestamp, addon_id, downloads, score) -> None:
        super().__init__()
        self.timestamp = timestamp
        self.addon_id = addon_id
        self.downloads = downloads
        self.score = score

    @classmethod
    def add_from_model(cls, timestamp: datetime, addon: AddonModel):
        return cls.add(timestamp, addon.addon_id, addon.downloads, addon.score)

    @classmethod
    def get_all_last_before(cls, timestamp: datetime):
        if timestamp is None:
            timestamp = datetime.now()
        return cls.query \
            .distinct(HistoricRecord.addon_id) \
            .filter(HistoricRecord.timestamp <= timestamp) \
            .order_by(HistoricRecord.addon_id, HistoricRecord.timestamp.desc()) \
            .all()

    @classmethod
    def get_last_before(cls, timestamp: datetime, addon_id: int):
        if timestamp is None:
            timestamp = datetime.now()
        return cls.query \
            .filter(HistoricRecord.addon_id == addon_id) \
            .filter(HistoricRecord.timestamp <= timestamp) \
            .order_by(HistoricRecord.timestamp.desc()) \
            .first()

    @classmethod
    def add(cls, timestamp: datetime, addon_id: int, downloads: int, score: float):
        if timestamp is None:
            timestamp = datetime.now()
        last = cls.get_last_before(timestamp, addon_id)
        if last is None or last.downloads != downloads or last.score != score:
            db.session.add(HistoricRecord(timestamp, addon_id, downloads, score))
            db.session.commit()
            return True
        return False
