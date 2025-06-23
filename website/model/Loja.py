from .. import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Loja(db.Model):
    __tablename__ = 'loja'
    id = db.Column(db.Integer, primary_key = True)
    endereco = db.Column(db.String(100))
    cnpj = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    nome = db.Column(db.String) 
    
    def __init__(self, endereco, cnpj, latitude, longitude, nome):
        self.endereco = endereco
        self.cnpj = cnpj
        self.latitude = latitude
        self.longitude = longitude
        self.nome = nome