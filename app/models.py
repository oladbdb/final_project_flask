from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.relationship('Role')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

equipment_responsible = db.Table(
    'equipment_responsible',
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True),
    db.Column('responsible_person_id', db.Integer, db.ForeignKey('responsible_person.id'), primary_key=True)
)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    inventory_number = db.Column(db.String(100), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('В эксплуатации', 'На ремонте', 'Списано'), nullable=False, default='В эксплуатации')
    comment = db.Column(db.Text)

    category = db.relationship('Category', backref='equipments')
    photo = db.relationship("Photo", back_populates="equipment", uselist=False, cascade='all, delete-orphan')
    service_records = db.relationship('ServiceHistory', backref='equipment', cascade='all, delete-orphan')
    responsible_persons = db.relationship('ResponsiblePerson', secondary=equipment_responsible, back_populates='equipments')

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False, unique=True)
    equipment = db.relationship("Equipment", back_populates="photo")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)

class ResponsiblePerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)

    equipments = db.relationship('Equipment', secondary=equipment_responsible, back_populates='responsible_persons')

