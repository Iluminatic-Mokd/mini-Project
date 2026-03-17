from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    trades = db.relationship("Trade", backref="user", lazy=True)

class Trade(db.Model):
    __tablename__ = "trades"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    asset = db.Column(db.String(50), nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    entry = db.Column(db.Float, nullable=False)
    exit = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    take_profit = db.Column(db.Float, nullable=True)
    size = db.Column(db.Float, nullable=True)
    strategy = db.Column(db.String(100), nullable=True)
    screenshot = db.Column(db.String(250), nullable=True)
    rr = db.Column(db.Float, nullable=True)
    result = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)