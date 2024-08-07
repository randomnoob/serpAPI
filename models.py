from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SerpData(db.Model):
    __tablename__ = 'serp_data'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), nullable=False)
    serp_page = db.Column(db.Text, nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    top1_match = db.Column(db.Boolean, default=False)