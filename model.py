from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lokasi = db.Column(db.String(30),nullable=False)
    jenis = db.Column(db.String(30),nullable=False)
    track_id = db.Column(db.Integer,nullable=False)
    waktu = db.Column(db.DateTime,nullable=False,default = datetime.now)
    
    def __repr__(self):
        return f'<Counter id={self.id}, lokasi={self.lokasi}, jenis={self.jenis},waktu={self.waktu}>'
    