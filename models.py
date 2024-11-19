from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)