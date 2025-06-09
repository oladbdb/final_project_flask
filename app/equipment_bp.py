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

@equipment_bp.route('/<int:equipment_id>')
@login_required
@check_rights('view_equipment')
def view_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    return render_template('view_equipment.html', equipment=equipment)

@equipment_bp.route('/<int:equipment_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights('edit_equipment')
def edit_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    categories = Category.query.all()
    responsible_persons = ResponsiblePerson.query.all()
    if request.method == 'POST':
        equipment.name = request.form.get('name')
        equipment.inventory_number = request.form.get('inventory_number')
        equipment.category_id = request.form.get('category_id')
        purchase_date = request.form.get('purchase_date') or None
        equipment.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d') if purchase_date else None
        equipment.cost = request.form.get('cost') or None
        equipment.status = request.form.get('status')
        equipment.note = request.form.get('note')

        responsible_ids = request.form.getlist('responsible_persons')
        equipment.responsible_persons = ResponsiblePerson.query.filter(ResponsiblePerson.id.in_(responsible_ids)).all()

        try:
            db.session.commit()
            flash('Оборудование обновлено', 'success')
            return redirect(url_for('equipment.view_equipment', equipment_id=equipment.id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении', 'danger')

    data = {
        'name': equipment.name,
        'inventory_number': equipment.inventory_number,
        'category_id': str(equipment.category_id),
        'purchase_date': equipment.purchase_date.strftime('%Y-%m-%d') if equipment.purchase_date else '',
        'cost': str(equipment.cost) if equipment.cost else '',
        'status': equipment.status,
        'note': equipment.note,
        'responsible_persons': [str(p.id) for p in equipment.responsible_persons]
    }

    return render_template('equipment_form.html', title='Редактировать оборудование', categories=categories, responsible_persons=responsible_persons, data=data)



@equipment_bp.route('/<int:equipment_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_equipment')
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)

    try:
        db.session.delete(equipment)
        db.session.commit()
        flash('Оборудование удалено', 'success')
    except:
        db.session.rollback()
        flash('Ошибка при удалении оборудования.', 'danger')

    return redirect(url_for('equipment.equipment_list'))


@equipment_bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_equipment')
def create_user():
    categories = Category.query.all()
    responsible_persons = ResponsiblePerson.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        inventory_number = request.form.get('inventory_number')
        category_id = request.form.get('category_id')
        purchase_date = request.form.get('purchase_date') or None
        cost = request.form.get('cost')
        status = request.form.get('status')
        note = request.form.get('note')

        responsible_ids = request.form.getlist('responsible_persons')

        new_equipment = Equipment(
            name=name,
            inventory_number=inventory_number,
            category_id=category_id,
            purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d') if purchase_date else None,
            cost=cost,
            status=status,
            note=note
        )

        new_equipment.responsible_persons = ResponsiblePerson.query.filter(ResponsiblePerson.id.in_(responsible_ids)).all()

         # Фото
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename:
            file_data = photo_file.read()
            md5_hash = hashlib.md5(file_data).hexdigest()

            existing_photo = Photo.query.filter_by(md5_hash=md5_hash).first()

            if not existing_photo:
                # Сохраняем файл
                filename = photo_file.filename
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                photo = Photo(
                    file_name=filename,
                    mime_type=photo_file.mimetype,
                    md5_hash=md5_hash
                )
                new_equipment.photos.append(photo)
            else:
                # Используем существующее фото
                new_equipment.photos.append(existing_photo)

        try:
            db.session.add(new_equipment)
            db.session.commit()
            flash('Оборудование успешно добавлено!', 'success')
            return redirect(url_for('equipment.equipment_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении оборудования.', 'danger')
            return render_template('equipment_form.html', title='Добавить оборудование', form_action='create_equipment', categories=categories, responsible_persons=responsible_persons, data={})

    return render_template('equipment_form.html', title='Добавить оборудование', form_action='create_equipment', categories=categories, responsible_persons=responsible_persons, data={})

# --- Добавить запись об обслуживании ---
@equipment_bp.route('/<int:equipment_id>/add_service', methods=['GET', 'POST'])
@login_required
@check_rights('create_service')
def add_service_record(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)

    if request.method == 'POST':
        date = request.form.get('date') or datetime.now().date()
        service_type = request.form.get('service_type')
        comment = request.form.get('comment')

        new_service = ServiceHistory(
            equipment_id=equipment.id,
            date=datetime.strptime(date, '%Y-%m-%d'),
            service_type=service_type,
            comment=comment
        )

        try:
            db.session.add(new_service)
            db.session.commit()
            flash('Запись об обслуживании добавлена', 'success')
            return redirect(url_for('equipment.view_equipment', equipment_id=equipment.id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении записи об обслуживании.', 'danger')

    return render_template('service_form.html', equipment=equipment)