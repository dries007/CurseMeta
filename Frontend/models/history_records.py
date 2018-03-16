import os.path
import json

from datetime import datetime

from .. import db

from .current_records import AddonModel


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


def read_old_history_folder(basepath):
    with open(os.path.join(basepath, 'index.json'), 'r') as f:
        data = json.load(f)['history']

    indexes = {}
    downloads = {}

    n = len(data)
    print('Found', n, 'timestamps')
    for i, timestamp in enumerate(sorted(data)):
        print('Working on', i, 'of', n, ':', timestamp)
        with open(os.path.join(basepath, '{}.json'.format(timestamp)), 'r') as f:
            data = json.load(f)
        timestamp = datetime.fromtimestamp(timestamp)
        for k, v in data.items():
            k = int(k)
            if k not in indexes:
                indexes[k] = AddonModel.query.get(k) is not None
            if not indexes[k]:
                continue
            if k not in downloads or downloads[k] != v:
                downloads[k] = v
                db.session.merge(HistoricRecord(timestamp, k, v, None))
                db.session.commit()


def read_old_history_file(basepath, timestamp: int):
    with open(os.path.join(basepath, '{}.json'.format(timestamp)), 'r') as f:
        data = json.load(f)

    for k, v in data.items():
        HistoricRecord.add(datetime.fromtimestamp(timestamp), k, v, None)

    db.session.commit()
