from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from permission import check_rights
from models import db, User, Equipment, Category, Photo, ResponsiblePerson, ServiceHistory
from sqlalchemy import func
from datetime import datetime
import hashlib
import os

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

# Папка для хранения загруженных файлов
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@equipment_bp.route('/')
@login_required
@check_rights('view_equipment')
def equipment_list():
    equipment = Equipment.query.all()
    return render_template('equipment_list.html', equipment=equipment)



