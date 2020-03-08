from app import db
from flask import url_for
from datetime import datetime

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, index=True)    
    restr_id = db.Column(db.Integer, index=True)
    table_id = db.Column(db.Integer, index=True)
    booking_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(db.String(10), default="booked")

    def __repr__(self):
        return '<Booking Id {}>'.format(self.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'restr_id': self.restr_id,
            'table_id': self.table_id,
            'booking_time': self.booking_time,
            'status': self.status,
            '_links': {                    
            'self': url_for('api.booking', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['user_id', 'restr_id', 'table_id']:
            setattr(self, field, data[field])
