from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Equipment, ServiceHistory
from datetime import datetime
from permission import check_rights

service_bp = Blueprint('service', __name__, url_prefix='/service')

@service_bp.route('/')
@login_required
def service_list():
    services = ServiceHistory.query.order_by(ServiceHistory.date.desc()).all()
    return render_template('service.html', services=services)

@service_bp.route('/add', methods=['GET', 'POST'])
@service_bp.route('/add/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
@check_rights('create_service')
def add_service(equipment_id=None):
    equipments = Equipment.query.all()
    return_to = request.args.get('return_to', 'service.service_list')
    selected_equipment = Equipment.query.get(equipment_id) if equipment_id else None

    if request.method == 'POST':
        eq_id = equipment_id or int(request.form['equipment_id'])
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        service_type = request.form['service_type']
        comment = request.form.get('comment')

        new_record = ServiceHistory(
            equipment_id=eq_id,
            date=date,
            service_type=service_type,
            comment=comment
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Запись добавлена', 'success')

        return redirect(url_for(return_to))

    return render_template(
        'add_service.html',
        equipments=equipments,
        selected_equipment=selected_equipment,
        return_to=return_to
    )