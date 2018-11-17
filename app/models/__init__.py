import sqlalchemy_utils as sau

from datetime import datetime

from .. import db
from enum import IntEnum


author_addon_table = db.Table('author_addon', db.Model.metadata,
                              db.Column('author', db.String, db.ForeignKey('author.name')),
                              db.Column('addon', db.Integer, db.ForeignKey('addon.addon_id')))
category_addon_table = db.Table('category_addon', db.Model.metadata,
                                db.Column('category', db.Integer, db.ForeignKey('category.category_id')),
                                db.Column('addon', db.Integer, db.ForeignKey('addon.addon_id')))


def _do_update(data_map, obj, data, skip_keys_extra=('id',)):
    """
    Updates Model based object with provided data.
    Any missing data is skipped, any extra data is added to the extra field in the object. (Must be present!)

    :param data_map: Data<>Object mapping in form of {str: db.Column or (db.Column, callable)}
    :param obj: Object to act on
    :param data: Data dictionary
    :param skip_keys_extra: Any keys that are skipped from the 'extra' data field
    """
    for k, json_map in data_map.items():
        if k not in data:
            continue
        v = data[k]
        if isinstance(json_map, tuple):
            col, func = json_map
            v = func(v, obj, data)
        else:
            col = json_map
        setattr(obj, col.name, v)
    obj.extra = {
        k: data[k]
        for k in data.keys() - data_map.keys()
        if k not in skip_keys_extra and k in data and data[k] is not None
    }


class ReleaseTypeEnum(IntEnum):
    Release = 1
    Beta = 2
    Alpha = 3


class FileStatusEnum(IntEnum):
    Normal = 1,
    SemiNormal = 2,
    Reported = 3,
    Malformed = 4,
    Locked = 5,
    InvalidLayout = 6,
    Hidden = 7,
    NeedsApproval = 8,
    Deleted = 9,
    UnderReview = 10,
    MalwareDetected = 11,
    WaitingOnProject = 12,
    ClientOnly = 13,


class AddonStatusEnum(IntEnum):
    Normal = 1
    Hidden = 2
    Deleted = 3


class AddonStageEnum(IntEnum):
    Alpha = 1
    Beta = 2
    Deleted = 3
    Inactive = 4
    Mature = 5
    Planning = 6
    Release = 7
    Abandoned = 8


class PackageTypeEnum(IntEnum):
    Folder = 1
    Ctoc = 2
    SingleFile = 3
    Cmod2 = 4
    ModPack = 5
    Mod = 6


class AuthorModel(db.Model):
    __tablename__ = 'author'
    # The basics
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    name = db.Column(db.String, primary_key=True)
    # Relationships
    # primary_addons via backref
    # addons via backref

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @classmethod
    def update(cls, data: dict, commit=True):
        obj = cls.query.get(data['name'])
        if obj is None:
            obj = cls(data['name'])
            db.session.add(obj)
        if commit:
            db.session.commit()
        return obj


class FileModel(db.Model):
    __tablename__ = 'file'
    # The basics
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    file_id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), nullable=False)
    name = db.Column(db.String, nullable=True)
    url = db.Column(sau.URLType, nullable=True)
    # Easy to store & useful data
    date = db.Column(db.DateTime, nullable=True)
    release_type = db.Column(db.Enum(ReleaseTypeEnum), nullable=True)
    file_status = db.Column(db.Enum(FileStatusEnum), nullable=True)
    alternate = db.Column(db.Boolean, nullable=True)
    available = db.Column(db.Boolean, nullable=True)
    alternate_file_id = db.Column(db.Integer, nullable=True)
    # alternate_file_id = db.Column(db.Integer, db.ForeignKey(file_id), nullable=True)
    game_versions = db.Column(db.ARRAY(db.String), nullable=True)
    # todo: dependencies?
    # Anything extra
    extra = db.Column(db.JSON, nullable=True)
    # Relationships
    # alternate_file = db.relationship('FileModel', foreign_keys=[alternate_file_id], lazy='dynamic')
    # addon provided via backref.

    _JSON_MAP = {
        'fileNameOnDisk': name,
        'downloadUrl': url,
        'fileDate': date,
        'releaseType': release_type,
        'fileStatus': file_status,
        'isAlternate': alternate,
        'isAvailable': available,
        'alternateFileId': (alternate_file_id, lambda v, obj, data: v if v else None),
        'gameVersion': game_versions,
    }
    _SKIP_KEYS = (
        'id',
        'fileName',
    )

    def __init__(self, id_: int, addon_id: int, commit=True):
        super().__init__()
        self.file_id = id_
        self.addon_id = addon_id

        if AddonModel.query.get(addon_id) is None:
            # Don't fill in any data here, it'll get periodically filled in by a background task.
            db.session.add(AddonModel(addon_id))
            if commit:
                db.session.commit()

    @classmethod
    def update(cls, addon_id: int, data: dict, commit=True):
        obj = cls.query.get(data['id'])
        if obj is None:
            obj = cls(data['id'], addon_id)
            db.session.add(obj)

        # if obj.alternate_file_id != data['alternateFileId'] and cls.query.get(data['alternateFileId']) is None:
            # Don't fill in any data here, it'll get periodically filled in by a background task.
            # db.session.add(cls(data['alternateFileId'], addon_id, commit=False))

        _do_update(cls._JSON_MAP, obj, data, skip_keys_extra=cls._SKIP_KEYS)
        if commit:
            db.session.commit()
        return obj


class AttachmentModel(db.Model):
    __tablename__ = 'attachment'
    # The basics
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    attachment_id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), nullable=False)
    # Easy to store & useful data
    description = db.Column(db.String, nullable=True)
    default = db.Column(db.Boolean, nullable=True)
    thumbnail_url = db.Column(sau.URLType, nullable=True)
    title = db.Column(db.String, nullable=True)
    url = db.Column(sau.URLType, nullable=True)
    # Anything extra
    extra = db.Column(db.JSON, nullable=True)
    # Relationships
    # addon provided via backref.

    _JSON_MAP = {
        'projectID': addon_id,
        'description': description,
        'isDefault': default,
        'thumbnailUrl': thumbnail_url,
        'title': title,
        'url': url,
    }

    def __init__(self, id_: int):
        super().__init__()
        self.attachment_id = id_

    @classmethod
    def update(cls, data: dict, commit=True):
        obj = cls.query.get(data['id'])
        if obj is None:
            obj = cls(data['id'])
            db.session.add(obj)

        _do_update(cls._JSON_MAP, obj, data)
        if commit:
            db.session.commit()
        return obj


class CategoryModel(db.Model):
    __tablename__ = 'category'
    # The basics
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    url = db.Column(sau.URLType, nullable=True)
    # Easy to store & useful data
    parent_id = db.Column(db.Integer, db.ForeignKey(category_id), nullable=True)
    slug = db.Column(db.String, nullable=True)
    avatar_url = db.Column(sau.URLType, nullable=True)
    modified = db.Column(db.DateTime, nullable=True)
    # todo: make gameIDs a relation with foreign keys
    # Anything extra
    extra = db.Column(db.JSON, nullable=True)
    # Relationships
    parent = db.relationship('CategoryModel', foreign_keys=[parent_id], lazy='dynamic')
    # addons via backref

    _JSON_MAP = {
        'name': name,
        'url': url,
        'parentId': parent_id,
        'slug': slug,
        'avatarUrl': avatar_url,
        'dateModified': modified,
    }

    def __init__(self, id_: int):
        super().__init__()
        self.attachment_id = id_

    @classmethod
    def update(cls, data: dict, commit=True):
        obj = cls.query.get(data['id'])
        if obj is None:
            obj = cls(data['id'])
            db.session.add(obj)

        _do_update(cls._JSON_MAP, obj, data)

        if commit:
            db.session.commit()
        return obj


# todo: Game model
# todo: Section model
# todo: GameVersionLatestFile model


class AddonModel(db.Model):
    __tablename__ = 'addon'
    # The basics
    last_update = db.Column(db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    addon_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    game_id = db.Column(db.Integer, nullable=True)  # todo: make FK with relation
    # Easy to store & useful data
    # primary_author_name = db.Column(db.String, db.ForeignKey(AuthorModel.name, onupdate='cascade', ondelete='cascade'), nullable=True)
    primary_author_name = db.Column(db.String, nullable=True)
    category_list = db.Column(db.String, nullable=True)
    slug = db.Column(db.String, nullable=True)
    downloads = db.Column(db.BigInteger, nullable=True)
    score = db.Column(db.Float, nullable=True)
    summary = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    modified = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, nullable=True)
    released = db.Column(db.DateTime, nullable=True)
    available = db.Column(db.Boolean, nullable=True)
    featured = db.Column(db.Boolean, nullable=True)
    url = db.Column(sau.URLType, nullable=True)
    default_file_id = db.Column(db.Integer, nullable=True)
    # default_file_id = db.Column(db.Integer, db.ForeignKey(FileModel.file_id), nullable=True)
    status = db.Column(db.Enum(AddonStatusEnum), nullable=True)
    stage = db.Column(db.Enum(AddonStageEnum), nullable=True)
    section_id = db.Column(db.Integer, nullable=True)  # todo: make FK with relation
    package_type = db.Column(db.Enum(PackageTypeEnum), nullable=True)
    # todo: add gameVersionLatestFiles

    # Anything extra
    extra = db.Column(db.JSON, nullable=True)
    # Relationships
    files = db.relationship(FileModel, backref='addon', foreign_keys=[FileModel.addon_id], lazy='dynamic')
    attachments = db.relationship(AttachmentModel, backref='addon', lazy='dynamic')
    # default_file = db.relationship(FileModel, foreign_keys=[default_file_id], lazy='select')
    # primary_author = db.relationship(AuthorModel, foreign_keys=[primary_author_name], backref='primary_addons', lazy='select')
    authors = db.relationship(AuthorModel, secondary=author_addon_table, backref='addons', lazy='dynamic')
    categories = db.relationship(CategoryModel, secondary=category_addon_table, backref='addons', lazy='dynamic')

    _JSON_MAP = {
        'name': name,
        'gameId': game_id,
        'primaryAuthorName': primary_author_name,
        'categoryList': category_list,
        'slug': slug,
        'downloadCount': downloads,
        'popularityScore': score,
        'summary': summary,
        'fullDescription': description,
        'dateModified': modified,
        'dateCreated': created,
        'dateReleased': released,
        'isAvailable': available,
        'isFeatured': featured,
        'websiteUrl': url,
        'defaultFileId': (default_file_id, lambda v, obj, data: v if v != 0 else None),
        'status': status,
        'stage': stage,
        'categorySection': (section_id, lambda v, obj, data: v['Id']),
        'packageType': package_type,
    }
    _SKIP_KEYS = (
        'id',
        'clientUrl',
        'gameName',
        'portalName',
        'sectionName',
        'gamePopularityRank',
        'authors',
        'attachments',
        'latestFiles',
    )

    def __init__(self, id_: int):
        super().__init__()
        self.addon_id = id_

    @classmethod
    def update(cls, data: dict, commit=True):
        obj = cls.query.get(data['id'])
        if obj is None:
            obj = cls(data['id'])
            db.session.add(obj)
        obj.update_direct(data, commit)
        return obj

    def update_direct(self, data: dict, commit=True, skip_some=False):
        if not skip_some:
            if data['authors']:
                for author in data['authors']:
                    author = AuthorModel.update(author, commit=False)
                    if author not in self.authors:
                        self.authors.append(author)
            if data['attachments']:
                for attachment in data['attachments']:
                    attachment = AttachmentModel.update(attachment, commit=False)
                    if attachment not in self.attachments:
                        self.attachments.append(attachment)

        if data['latestFiles']:
            for file in data['latestFiles']:
                FileModel.update(data['id'], file, commit=False)

        _do_update(self._JSON_MAP, self, data, skip_keys_extra=self._SKIP_KEYS)
        if commit:
            db.session.commit()
        return self


class HistoricDayRecord(db.Model):
    __tablename__ = 'history_day'
    date = db.Column(db.Date, nullable=False, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    downloads = db.Column(db.BigInteger)
    score = db.Column(db.Float)

    def __init__(self, date_, addon: AddonModel):
        super().__init__()
        self.date = date_
        self.addon_id = addon.addon_id
        self.downloads = addon.downloads
        self.score = addon.score


class HistoricRecord(db.Model):
    __tablename__ = 'history'
    timestamp = db.Column(db.DateTime, nullable=False, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.addon_id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    downloads = db.Column(db.BigInteger)
    score = db.Column(db.Float)

    # def __init__(self, timestamp, addon_id, downloads, score) -> None:
    #     super().__init__()
    #     self.timestamp = timestamp
    #     self.addon_id = addon_id
    #     self.downloads = downloads
    #     self.score = score

    def __init__(self, timestamp, addon: AddonModel):
        super().__init__()
        self.timestamp = timestamp
        self.addon_id = addon.addon_id
        self.downloads = addon.downloads
        self.score = addon.score

    # @classmethod
    # def add_from_model(cls, timestamp: datetime, addon: AddonModel):
    #     return cls.add(timestamp, addon.addon_id, addon.downloads, addon.score)
    #
    # @classmethod
    # def get_all_last_before(cls, timestamp: datetime):
    #     if timestamp is None:
    #         timestamp = datetime.now()
    #     return cls.query \
    #         .distinct(HistoricRecord.addon_id) \
    #         .filter(HistoricRecord.timestamp <= timestamp) \
    #         .order_by(HistoricRecord.addon_id, HistoricRecord.timestamp.desc()) \
    #         .all()
    #
    # @classmethod
    # def get_last_before(cls, timestamp: datetime, addon_id: int):
    #     if timestamp is None:
    #         timestamp = datetime.now()
    #     return cls.query \
    #         .filter(HistoricRecord.addon_id == addon_id) \
    #         .filter(HistoricRecord.timestamp <= timestamp) \
    #         .order_by(HistoricRecord.timestamp.desc()) \
    #         .first()
    #
    # @classmethod
    # def add(cls, timestamp: datetime, addon_id: int, downloads: int, score: float):
    #     if timestamp is None:
    #         timestamp = datetime.now()
    #     last = cls.get_last_before(timestamp, addon_id)
    #     if last is None or last.downloads != downloads or last.score != score:
    #         db.session.add(HistoricRecord(timestamp, addon_id, downloads, score))
    #         db.session.commit()
    #         return True
    #     return False
