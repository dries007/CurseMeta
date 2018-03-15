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
    def add(cls, timestamp: datetime, addon_id: int, downloads: int, score: float):
        last: HistoricRecord = cls.query\
            .filter(HistoricRecord.addon_id == addon_id) \
            .filter(HistoricRecord.timestamp <= timestamp) \
            .order_by(HistoricRecord.timestamp.desc()) \
            .first()

        if AddonModel.query.get(addon_id) is None:
            return

        if last is None or last.downloads != downloads or last.score != score:
            db.session.add(HistoricRecord(timestamp, addon_id, downloads, score))


def read_old_history_folder(basepath):
    with open(os.path.join(basepath, 'index.json'), 'r') as f:
        data = json.load(f)['history']
    n = len(data)
    print('Found', n, 'timestamps')
    for i, timestamp in enumerate(sorted(data)):
        print('Working on', i, 'of', n, ':', timestamp)
        try:
            read_old_history_file(basepath, timestamp)
        except Exception as e:
            print(e)


def read_old_history_file(basepath, timestamp: int):
    with open(os.path.join(basepath, '{}.json'.format(timestamp)), 'r') as f:
        data = json.load(f)

    for k, v in data.items():
        HistoricRecord.add(datetime.fromtimestamp(timestamp), k, v, None)

    db.session.commit()
