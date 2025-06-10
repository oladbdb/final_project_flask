from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Role, Equipment, Category, Photo, ServiceHistory, ResponsiblePerson
from werkzeug.security import generate_password_hash
from datetime import datetime
import pytz
import os
from equipment_bp import equipment_bp
from service_bp import service_bp


app = Flask(__name__)
app.secret_key = 'secret_key'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'instance', 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(equipment_bp)
app.register_blueprint(service_bp)

# Инициализация Flask-Login и БД
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db.init_app(app)
    
# Загрузка пользователя по id
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = Equipment.query

    if category_id:
        query = query.filter(Equipment.category_id == category_id)
    if status:
        query = query.filter(Equipment.status == status)
    if date_from:
        query = query.filter(Equipment.purchase_date >= date_from)
    if date_to:
        query = query.filter(Equipment.purchase_date <= date_to)

    equipment = query.order_by(Equipment.purchase_date.desc()).paginate(page=page, per_page=10)
    categories = Category.query.all()

    return render_template('index.html', equipment=equipment, categories=categories)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember' in request.form 
        
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash('Успешный вход!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html', title='Авторизация')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'info') 
    return redirect(url_for('index'))

@app.before_request
def init_db():
    db.create_all()
    if not Role.query.first():
        admin = Role(
            name='Admin', 
            description='Роль администратора. Полный доступ (добавление, редактирование, удаление)'
        )
        tech = Role(
            name='Technician',
            description='Роль технического специалиста. Просмотр, добавление записей об обслуживании.'
        )
        default = Role(
            name='Default_User',
            description='Роль обычного пользователя. Только просмотр.'
        )
        db.session.add_all([admin, tech, default])
        db.session.commit()

    if not User.query.first():
        default_user = User(
            username='user', 
            password=generate_password_hash('qwerty'),
            first_name='Имя',
            last_name='Фамилия',
            patronymic='Отчество',
            role_id = 1
            )
        tech_user = User(
            username='tech', 
            password=generate_password_hash('qwerty'),
            first_name='Имя',
            last_name='Фамилия',
            patronymic='Отчество',
            role_id = 2
            )
        user = User(
            username='test_user', 
            password=generate_password_hash('qwerty'),
            first_name='Имя',
            last_name='Фамилия',
            patronymic='Отчество',
            role_id = 3
            )
        db.session.add_all([default_user, tech_user, user])
        db.session.commit()
    
    # Категории
    if not Category.query.first():
        categories = [
            Category(name='Принтеры', description='Лазерные и струйные принтеры'),
            Category(name='Сканеры', description='Сканеры документов'),
            Category(name='Компьютеры', description='Настольные ПК и ноутбуки'),
            Category(name='Мониторы', description='Мониторы'),
            Category(name='Сетевое оборудование', description='Маршрутизаторы, коммутаторы'),
        ]
        db.session.add_all(categories)
        db.session.commit()

    # Ответственные лица
    if not ResponsiblePerson.query.first():
        persons = [
            ResponsiblePerson(full_name='Иванов Иван Иванович', position='Системный администратор', contact_info='ivanov@example.com'),
            ResponsiblePerson(full_name='Петров Петр Петрович', position='Техник', contact_info='petrov@example.com'),
            ResponsiblePerson(full_name='Сидорова Анна Сергеевна', position='Менеджер', contact_info='sidorova@example.com'),
        ]
        db.session.add_all(persons)
        db.session.commit()

    # Оборудование
    if not Equipment.query.first():
        categories = {c.name: c for c in Category.query.all()}
        persons = ResponsiblePerson.query.all()

        e1 = Equipment(name='Принтер HP LaserJet P1102', inventory_number='INV-1001', category_id=categories['Принтеры'].id, purchase_date=datetime(2021, 5, 12), cost=12000.00, status='В эксплуатации')
        e1.responsible_persons = [persons[0]]
        e2 = Equipment(name='Сканер Canon CanoScan LiDE 300', inventory_number='INV-1002', category_id=categories['Сканеры'].id, purchase_date=datetime(2022, 3, 20), cost=8500.00, status='В эксплуатации')
        e2.responsible_persons = [persons[2]]
        e3 = Equipment(name='Ноутбук Lenovo ThinkPad E15', inventory_number='INV-1003', category_id=categories['Компьютеры'].id, purchase_date=datetime(2023, 1, 15), cost=75000.00, status='В эксплуатации')
        e3.responsible_persons = [persons[0], persons[1]]
        e4 = Equipment(name='Монитор Samsung S24F354FHI', inventory_number='INV-1004', category_id=categories['Мониторы'].id, purchase_date=datetime(2020, 9, 10), cost=10500.00, status='На ремонте')
        e4.responsible_persons = [persons[1]]
        e5 = Equipment(name='Маршрутизатор MikroTik hAP', inventory_number='INV-1005', category_id=categories['Сетевое оборудование'].id, purchase_date=datetime(2019, 7, 5), cost=6500.00, status='Списано')
        e5.responsible_persons = [persons[0]]
        e6 = Equipment(name='Компьютер Dell OptiPlex 3080', inventory_number='INV-1006', category_id=categories['Компьютеры'].id, purchase_date=datetime(2022, 2, 10), cost=56000.00, status='В эксплуатации')
        e6.responsible_persons = [persons[2]]
        e7 = Equipment( name='Монитор LG 27MK400H-B', inventory_number='INV-1007', category_id=categories['Мониторы'].id, purchase_date=datetime(2021, 8, 22), cost=14500.00, status='В эксплуатации')
        e7.responsible_persons = [persons[2]]
        e8 = Equipment(name='Принтер Brother HL-1223WR', inventory_number='INV-1008', category_id=categories['Принтеры'].id, purchase_date=datetime(2022, 12, 2), cost=9700.00, status='В эксплуатации')
        e8.responsible_persons = [persons[1]]
        e9 = Equipment(name='Ноутбук HP ProBook 450 G8', inventory_number='INV-1009', category_id=categories['Компьютеры'].id, purchase_date=datetime(2023, 4, 1), cost=82000.00, status='В эксплуатации')
        e9.responsible_persons = [persons[0]]
        e10 = Equipment(name='Сканер Epson Perfection V39', inventory_number='INV-1010', category_id=categories['Сканеры'].id, purchase_date=datetime(2020, 6, 17), cost=11000.00, status='В эксплуатации')
        e10.responsible_persons = [persons[2]]
        e11 = Equipment(name='Маршрутизатор TP-Link Archer AX10', inventory_number='INV-1011', category_id=categories['Сетевое оборудование'].id, purchase_date=datetime(2021, 11, 10), cost=9500.00, status='В эксплуатации')
        e11.responsible_persons = [persons[0]]
        e12 = Equipment(name='Монитор ASUS VG249Q', inventory_number='INV-1012', category_id=categories['Мониторы'].id, purchase_date=datetime(2022, 5, 18), cost=23000.00, status='В эксплуатации')
        e12.responsible_persons = [persons[2]]
        e13 = Equipment(name='Сервер Dell PowerEdge T40', inventory_number='INV-1013', category_id=categories['Компьютеры'].id, purchase_date=datetime(2021, 8, 25), cost=125000.00, status='В эксплуатации')
        e13.responsible_persons = [persons[0], persons[1]]
        e14 = Equipment( name='Принтер Xerox Phaser 3020BI', inventory_number='INV-1014', category_id=categories['Принтеры'].id, purchase_date=datetime(2023, 2, 14), cost=11500.00, status='В эксплуатации')
        e14.responsible_persons = [persons[1]]
        e15 = Equipment(name='Сканер Brother ADS-1200', inventory_number='INV-1015', category_id=categories['Сканеры'].id, purchase_date=datetime(2020, 9, 30), cost=17800.00, status='В эксплуатации')
        e15.responsible_persons = [persons[2]]

        db.session.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12, e13, e14, e15])
        db.session.commit()

    # История обслуживания
    if not ServiceHistory.query.first():
        e1 = Equipment.query.filter_by(inventory_number='INV-1001').first()
        e3 = Equipment.query.filter_by(inventory_number='INV-1003').first()
        e4 = Equipment.query.filter_by(inventory_number='INV-1004').first()
        s1 = ServiceHistory(equipment_id=e1.id, date=datetime(2023, 7, 15), service_type='Замена картриджа', comment='Установлен новый оригинальный картридж')
        s2 = ServiceHistory(equipment_id=e3.id, date=datetime(2024, 1, 10), service_type='Профилактическая чистка', comment='Очистка системы охлаждения')
        s3 = ServiceHistory( equipment_id=e4.id, date=datetime(2024, 3, 5), service_type='Диагностика', comment='Диагностирована проблема с подсветкой, требуется замена блока питания')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(base_dir, 'uploads'), filename)

if __name__ == '__main__':
    app.run(debug=True)
