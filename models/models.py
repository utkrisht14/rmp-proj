from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    address = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    salary = db.Column(db.Float)
    department = db.Column(db.String(50))