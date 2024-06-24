from flask import Flask, render_template, request, url_for, session, redirect, url_for, flash, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import csrf
import asyncio
import websockets
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from werkzeug.security import generate_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import generate_csrf, CSRFProtect
from flask_wtf.csrf import CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash
from urllib.parse import quote_plus, unquote_plus
import bleach
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from docx import Document
import secrets
import string
import plotly
import plotly.graph_objs as go
import json
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from collections import Counter

app = Flask(__name__)

# Настройки базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = '12345'
app.config['WTF_CSRF_ENABLED'] = True
db = SQLAlchemy(app)

csrf = CSRFProtect(app)
def create_app():
    app = Flask(__name__)
    csrf.init_app(app)


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

#_______________________________________________________________________________
#БАЗА ДАННЫХ


user_institutions = db.Table('user_institutions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('institution_id', db.Integer, db.ForeignKey('institutions.id'))
)

courses_institutions = db.Table('courses_institutions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('institution_id', db.Integer, db.ForeignKey('institutions.id'))
)

course_authors = db.Table('course_authors',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('users.id'))
)

class User(UserMixin, db.Model):
     __tablename__ = 'users'
     id = db.Column(db.Integer, primary_key=True)
     login = db.Column(db.Text, nullable=False, unique = True)
     password = db.Column(db.Text, nullable=False)
     mail = db.Column(db.Text, nullable = True, unique = True)
     name = db.Column(db.Text, nullable=False) #офиц имя
     role = db.Column(db.Text, nullable=False) #статус пользователя: права
     created_at = db.Column(db.DateTime, default=datetime.utcnow) #время создания пользователя

     institutions = db.relationship('Institution', secondary=user_institutions, backref='users')#заведения
     courses = db.relationship('Course', secondary=course_authors, backref='authors')  # курсы


class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, default='название заведения') #название заведения
    type = db.Column(db.Text, nullable=True, default='тип заведения') #тип заведения: предприятие, университет, бизнес  и тд. свободная форма

    courses = db.relationship('Course', secondary=courses_institutions, backref='institutions')


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, default='название курса')
    description = db.Column(db.Text, nullable=True)
    equipments = db.Column(db.Text, nullable=True)
    language = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Text, nullable=True)
    initial_requirements = db.Column(db.Text, nullable=True)

class CourseCode(db.Model):
    __tablename__ = 'course_codes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)

class CourseCompletion(db.Model):
    __tablename__ = 'course_completions'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    completion_status = db.Column(db.String, default='False')
    points = db.Column(db.Integer, default = 0)
    grade = db.Column(db.Text, nullable=True)

class Topic(db.Model): #Темы
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False , default='название темы')
    index = db.Column(db.Integer, nullable=False) #порядок отображения

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)

class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    correct_answer = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), unique=True)

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text, nullable=False)
    option4 = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), unique=True)

class Element(db.Model):
    __tablename__ = 'elements'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    element_type = db.Column(db.Text, nullable=False)  # Лекция или Задание
    element_id = db.Column(db.Integer, nullable=False)  # Внешний ключ к Лекции или Заданию

    __table_args__ = (
        db.CheckConstraint(element_type.in_(['Лекция', 'Задание'])),
    )

    # Полиморфное отношение к Лекции
    lecture = relationship("Lecture", primaryjoin="and_(Element.element_id==Lecture.id, "
                                                  "Element.element_type=='Лекция')",
                           uselist=False, foreign_keys=[element_id])

    # Полиморфное отношение к Заданию
    task = relationship("Task", primaryjoin="and_(Element.element_id==Task.id, "
                                            "Element.element_type=='Задание')",
                        uselist=False, foreign_keys=[element_id])


class ChatMessenger1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

class GroupMembership(db.Model):
    __tablename__ = 'group_membership'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Support(db.Model):
    __tablename__ = 'supports'
    id = db.Column(db.Integer, primary_key=True)
    message_sup = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#_______________________________________________________________________________
#МАРШРУТИЗАТОРЫ
admin = Admin(app, name='Админ-панель', template_mode='bootstrap3')

# Создание пользовательского представления модели
class UserView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

class LectureView(ModelView):
    column_list = ('id', 'title', 'description')  # поля, которые будут отображаться в списке
    form_columns = ('title', 'description')  # поля, которые будут отображаться в форме

class SupportView(ModelView):
    column_list = ('id', 'message_sup', 'user_id')
    form_columns = ('message_sup', 'user_id')

# Добавление представления модели в админ-панель
admin.add_view(UserView(User, db.session))
admin.add_view(LectureView(Lecture, db.session))
admin.add_view(SupportView(Support, db.session))


clients = set()

async def handler(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            for client in clients:
                if client != websocket:
                    await client.send(message)
    finally:
        clients.remove(websocket)

async def main():
    async with websockets.serve(handler, 'localhost', 5000):
        await asyncio.Future()  # Run forever
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.template_filter('url_encode')
def url_encode_filter(s):
    return quote_plus(s)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = generate_password_hash(request.form['psw'])
        role = request.form['status']

        institution = Institution.query.filter_by(name='К(П)ФУ').first()
        if not institution:
            institution = Institution(name='название заведения', type='тип заведения')
            db.session.add(institution)
            db.session.commit()

        # Создание нового пользователя
        new_user = User(
            login=email,
            password=password,
            mail=email,
            name=fullname,
            role=role
        )
        # Добавление связи с учреждением
        new_user.institutions.append(institution)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('personal_area'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')

    return render_template('mainpage.html')

@app.route('/')
def mainpage():
    return render_template('mainpage.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainpage'))
@app.route('/personal_area', methods=['GET', 'POST'])
@login_required  # Защищаем этот маршрут для авторизованных пользователей
def personal_area():
    # Получаем текущего пользователя
    user = current_user
    # Получаем данные пользователя
    email = user.mail
    full_name = user.name
    role = user.role
    institution = user.institutions[0].name if user.institutions else "Не указано"

    if role == 'учащийся':
        # Получаем курсы, на которые зарегистрирован текущий учащийся
        courses = db.session.query(Course).join(CourseCompletion).filter(CourseCompletion.user_id == user.id).all()
    elif role == 'автор курса':
        # Получаем курсы, созданные текущим автором
        courses = db.session.query(Course).join(course_authors).filter(course_authors.c.author_id == user.id).all()
    else:
        # Логика для других ролей (например, администратор и т.д.)
        courses = []

    # Передаем данные в шаблон
    return render_template('PersonalArea.html', email=email, full_name=full_name, role=role,
                           institution=institution, courses=courses)

def role_required(role):
    def decorator(f):
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash('У вас нет доступа к этой странице.', 'danger')
                return redirect(url_for('mainpage'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/add_course')
def addcourse():
    return render_template('AddCourse.html')

@app.route('/add_course_by_code', methods=['POST'])
@login_required
def add_course_by_code():
    course_code = request.form.get('courseCode')
    course_code_entry = CourseCode.query.filter_by(code=course_code).first()

    if course_code_entry:
        existing_entry = CourseCompletion.query.filter_by(user_id=current_user.id, course_id=course_code_entry.course_id).first()
        if not existing_entry:
            new_completion = CourseCompletion(
                user_id=current_user.id,
                course_id=course_code_entry.course_id,
                completion_status='False'
            )
            db.session.add(new_completion)
            db.session.commit()
            flash('Курс успешно добавлен')
        else:
            flash('Вы уже зарегистрированы на этот курс')
    else:
        flash('Неверный код курса')

    return redirect(url_for('personal_area'))


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_er'
                           'ror.html', reason=e.description), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Ошибка: Файл не загружен', 400
    file = request.files['file']
    if file.filename == '':
        return 'Ошибка: Файл не выбран', 400
    file.save(os.path.join('uploads', file.filename))
    return 'Файл успешно загружен'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Получите данные формы входа из запроса
        mail = request.form['mail']
        password = request.form['password']

        user = User.query.filter_by(mail=mail).first()
        if user and check_password_hash(user.password, password):

            login_user(user)
            if user.mail == 'admin@example.com' and user.role == 'admin':
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('personal_area'))
        else:
            # Если учетные данные неверны, выведите сообщение об ошибке
            flash('Неправильный email или пароль', 'danger')
            return redirect(url_for('login'))  # Перенаправьте пользователя обратно на страницу входа

    # Если запрос метода GET, отобразите форму входа
    return render_template('mainpage.html')



@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    pass


@app.route('/create_course', methods=['POST'])
def create_course():
    name = request.form.get('courseName', 'название курса')
    description = request.form.get('courseDescription', None)
    equipments = request.form.get('equipments', None)
    language = request.form.get('language', None)
    difficulty = request.form.get('difficulty', None)
    duration = request.form.get('duration', None)
    initial_requirements = request.form.get('initial_requirements', None)

    new_course = Course(
        name=name,
        description=description,
        equipments=equipments,
        language=language,
        difficulty=difficulty,
        duration=duration,
        initial_requirements=initial_requirements
    )
    db.session.add(new_course)
    db.session.commit()

    institution_id = 1  # Замените на реальный ID учебного заведения
    new_course_institution = courses_institutions.insert().values(course_id=new_course.id, institution_id=institution_id)
    db.session.execute(new_course_institution)
    db.session.commit()

    new_course_author = course_authors.insert().values(course_id=new_course.id, author_id=current_user.id)
    db.session.execute(new_course_author)
    db.session.commit()

    # Добавление записи в таблицу CourseCode
    default_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    new_course_code = CourseCode(course_id=new_course.id, code=default_code)
    db.session.add(new_course_code)
    db.session.commit()

    flash('Курс успешно создан')
    return redirect(url_for('personal_area'))


class CourseDescriptionForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save')

@app.route('/support', methods=['POST'])
@login_required
def support():

    message_sup = request.form.get('message_sup')
    user_id = current_user.id
    new_support = Support(message_sup=message_sup, user_id=user_id)
    db.session.add(new_support)
    db.session.commit()
    flash('Ваше сообщение было отправлено!', 'success')
    return redirect(request.referrer)

@app.route('/course/update_description/<int:course_id>', methods=['POST'])
@login_required
def update_course_description(course_id):
    course = Course.query.get_or_404(course_id)
    new_description = request.form.get('description')

    if new_description:
        course.description = new_description
        db.session.commit()
        flash('Описание курса обновлено!', 'success')
    else:
        flash('Описание не может быть пустым.', 'error')

    return redirect(url_for('course_detail', name=quote_plus(course.name)))


@app.route('/get_messages', methods=['GET'])
@login_required
def get_messages():
    group_id = request.args.get('group_id')
    if group_id:
        messages = ChatMessenger1.query.filter_by(group_id=group_id).order_by(ChatMessenger1.send_time).all()
        return jsonify({'messages': [{'user_id': msg.user_id, 'message': msg.message} for msg in messages]})
    else:
        return jsonify({'error': 'Missing group_id parameter'}), 400
@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    try:
        message_content = request.form.get('message')
        group_id = request.form.get('group_id')

        if not message_content or not group_id:
            return 'Missing message content or group ID', 400

        new_message = ChatMessenger1(
            message=message_content,
            send_time=datetime.utcnow(),
            user_id=current_user.id,
            group_id=group_id
        )
        db.session.add(new_message)
        db.session.commit()
        return 'Message sent successfully', 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Error sending message', 500

def create_plot(course_id):
    data = db.session.query(CourseCompletion).filter_by(course_id=course_id).all()
    points = [row.points for row in data if row.points is not None]

    # Группировка баллов и подсчет количества учащихся для каждой группы
    points_count = Counter(points)
    sorted_points = sorted(points_count.items())

    # Подготовка данных для графика
    x = [item[0] for item in sorted_points]
    y = [item[1] for item in sorted_points]

    plot_data = [go.Bar(
        x=x,
        y=y
    )]

    layout = go.Layout(
        title='Распределение баллов по количеству учащихся',
        xaxis=dict(title='Баллы'),
        yaxis=dict(title='Количество учащихся')
    )

    fig = go.Figure(data=plot_data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_plot1(course_id):
    # Получаем данные из базы данных
    data = db.session.query(CourseCompletion).filter_by(course_id=course_id).all()

    # Извлекаем оценки
    grades = [float(row.grade) for row in data if row.grade is not None]

    # Считаем количество пользователей для каждой оценки
    grade_counts = Counter(grades)

    # Создаем круговую диаграмму
    plot_data = [go.Pie(
        labels=list(grade_counts.keys()),
        values=list(grade_counts.values())
    )]

    layout = go.Layout(
        title='Распределение оценок среди учащихся'
    )

    fig = go.Figure(data=plot_data, layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


# Обработчик для отображения информации о курсе
@app.route('/course/<name>',  methods=['GET', 'POST'])
@login_required
def course_detail(name):
    decoded_name = unquote_plus(name)
    course = Course.query.filter_by(name=decoded_name).first_or_404()
    course_code = CourseCode.query.filter_by(course_id=course.id).first().code
    form = CourseDescriptionForm()
    institutions = db.session.query(Institution).join(courses_institutions).filter(
        courses_institutions.c.course_id == course.id).all()
    # Выборка авторов курса
    authors = db.session.query(User).join(course_authors).filter(course_authors.c.course_id == course.id).all()
    students = db.session.query(User).join(CourseCompletion).filter(CourseCompletion.course_id == course.id).all()
    memberships = db.session.query(GroupMembership).join(Group).filter(Group.course_id == course.id).all()

    # Создание словаря с группами студентов
    student_groups = {}
    for membership in memberships:
        if membership.user_id not in student_groups:
            student_groups[membership.user_id] = []
        group_name = Group.query.filter_by(id=membership.group_id).first().name
        student_groups[membership.user_id].append(group_name)
    if request.method == 'GET':
        group_id = request.args.get('group_id')
        if group_id:
            messages = ChatMessenger1.query.filter_by(group_id=group_id).order_by(ChatMessenger1.send_time).all()
        else:
            messages = []

    if request.method == 'POST':
        if 'description' in request.form:
            # Обновление описания курса
            new_description = request.form.get('description')
            equipments = request.form.get('equipments').strip()
            language = request.form.get('language').strip()
            difficulty = request.form.get('difficulty').strip()
            duration = request.form.get('duration').strip()
            initial_requirements = request.form.get('initial_requirements').strip()

            if new_description:
                # Используем bleach для очистки HTML
                allowed_tags = ['b', 'i', 'u', 'strong', 'em']  # Разрешаем только основные теги форматирования
                cleaned_description = bleach.clean(new_description, tags=allowed_tags, strip=True)
                cleaned_description = cleaned_description.replace('&nbsp;', ' ')
                course.description = cleaned_description

                course.equipments = equipments
                course.language = language
                course.difficulty = difficulty
                course.duration = duration
                course.initial_requirements = initial_requirements

                db.session.commit()
                flash('Описание курса обновлено!', 'success')
            else:
                flash('Описание не может быть пустым.', 'error')

        elif 'topic_name' in request.form:
            # Добавление новой темы
            topic_name = request.form.get('topic_name')
            if topic_name:
                max_index = db.session.query(db.func.max(Topic.index)).filter_by(course_id=course.id).scalar() or 0
                new_topic = Topic(name=topic_name, index=max_index + 1, course_id=course.id)
                db.session.add(new_topic)
                db.session.commit()
                flash('Новая тема добавлена!', 'success')
            else:
                flash('Название темы не может быть пустым.', 'error')

        elif 'lecture_title' in request.form:
                # Загрузка новой лекции
                lecture_title = request.form.get('lecture_title')
                lecture_description = request.form.get('lecture_description')

                if not lecture_title or not lecture_description:
                    flash('Название и описание лекции обязательны для заполнения.', 'error')
                    return redirect(url_for('course_detail', name=name))

                # Создаем новую лекцию
                new_lecture = Lecture(title=lecture_title, description=lecture_description)
                db.session.add(new_lecture)
                db.session.commit()

                # Получаем ID текущей темы (нужно добавить логику для выбора текущей темы)
                topic_id = request.form.get('topic_id')

                # Создаем новый элемент и связываем его с темой и лекцией
                new_element = Element(topic_id=topic_id, element_type='Лекция', element_id=new_lecture.id)

                db.session.add(new_element)
                db.session.commit()

                flash('Лекция успешно добавлена!', 'success')
        elif 'group_name' in request.form:
            # Создание новой группы
            group_name = request.form.get('group_name')
            if group_name:
                new_group = Group(name=group_name, course_id=course.id)
                db.session.add(new_group)
                db.session.commit()
                flash('Новая группа добавлена!', 'success')
            else:
                flash('Название группы не может быть пустым.', 'error')

        elif 'group_id' in request.form and 'user_id' in request.form:

            user_id = request.form.get('user_id')
            group_id = request.form.get('group_id')

            if user_id and group_id:
                new_membership = GroupMembership(user_id=user_id, group_id=group_id)
                db.session.add(new_membership)
                db.session.commit()
                flash('Пользователь успешно добавлен в группу!', 'success')
            else:
                flash('Необходимо выбрать пользователя и группу.', 'error')

        elif 'group_id' in request.form:
            group_id = request.form.get('group_id')
            messages = ChatMessenger1.query.filter_by(group_id=group_id).order_by(ChatMessenger1.send_time).all()


        elif 'question' in request.form:
            question = request.form.get('question')

            if not question:
                flash('Вопрос обязателен для заполнения.', 'error')

                return redirect(url_for('course_detail', name=name))

            new_task = Task(question=question)
            db.session.add(new_task)
            db.session.commit()
            correct_answer = request.form.get('correct_answer')

            if correct_answer:
                new_answer = Answer(correct_answer=correct_answer, task_id=new_task.id)
                db.session.add(new_answer)
                db.session.commit()

            else:
                option1 = request.form.get('option1')
                option2 = request.form.get('option2')
                option3 = request.form.get('option3')
                option4 = request.form.get('option4')
                correct_option = request.form.get('correct_option')

                if not option1 or not option2 or not option3 or not option4 or not correct_option:
                    flash('Все варианты ответов обязательны для заполнения.', 'error')

                    return redirect(url_for('course_detail', name=name))

                new_test = Test(option1=option1, option2=option2, option3=option3, option4=option4,
                                correct_option=correct_option, task_id=new_task.id)

                db.session.add(new_test)
                db.session.commit()
            topic_id = request.form.get('topic_id')
            new_element = Element(topic_id=topic_id, element_type='Задание', element_id=new_task.id)
            db.session.add(new_element)
            db.session.commit()

            flash('Задание успешно добавлено!', 'success')

        elif 'answer' in request.form and 'task_id' in request.form:
            task_id = request.form.get('task_id')
            user_answer = request.form.get('answer')

            task = Task.query.get(task_id)
            element = Element.query.filter_by(element_id=task.id, element_type='Задание').first()
            topic_id = element.topic_id
            topic = Topic.query.get(topic_id)
            course_id = topic.course_id
            course_completion = CourseCompletion.query.filter_by(user_id=current_user.id, course_id=course_id).first()

            # Проверяем, прошел ли уже пользователь это задание
            if course_completion.points < task.id:
                test = Test.query.filter_by(task_id=task_id).first()
                if test:
                    correct_option = test.correct_option
                    if int(user_answer) == correct_option:
                        course_completion.points += 1
                        db.session.commit()
                        flash('Ваш ответ правильный!', 'success')
                    else:
                        flash('Ваш ответ неправильный.', 'error')
                else:
                    correct_answer = Answer.query.filter_by(task_id=task_id).first().correct_answer
                    if user_answer == correct_answer:
                        course_completion.points += 1
                        db.session.commit()
                        flash('Ваш ответ правильный!', 'success')
                    else:
                        flash('Ваш ответ неправильный.', 'error')

            total_tasks = Element.query.join(Topic).filter(Topic.course_id == course_id, Element.element_type == 'Задание').count()
            completed_tasks = course_completion.points
            if completed_tasks == total_tasks:
                course_completion.completion_status = "Завершен"
            elif completed_tasks != 0:
                course_completion.completion_status = "В процессе"
            course_completion.grade = (completed_tasks / total_tasks) * 100
            db.session.commit()

        return redirect(url_for('course_detail', name=name))

    topics = Topic.query.filter_by(course_id=course.id).order_by(Topic.index).all()
    edit_mode = request.args.get('edit') == 'true'
    groups = Group.query.filter_by(course_id=course.id).all()

    authors = course.authors
    author_details = [(author, author.institutions) for author in authors]
    institutions = course.institutions

    form = CourseDescriptionForm()
    form.description.data = course.description
    topics = Topic.query.filter_by(course_id=course.id).order_by(Topic.index).all()
    for topic in topics:
        elements = Element.query.filter_by(topic_id=topic.id, element_type='Лекция').all()
        topic.lectures = [element.lecture for element in elements]
    for topic in topics:
        elements = Element.query.filter_by(topic_id=topic.id, element_type='Задание').all()
        topic.tasks = [element.task for element in elements]
        for task in topic.tasks:
            task.test = Test.query.filter_by(task_id=task.id).first()
            task.answer = Answer.query.filter_by(task_id=task.id).first()

    if current_user.role == 'учащийся':
        courses = db.session.query(Course).join(CourseCompletion).filter(
            CourseCompletion.user_id == current_user.id).all()
    else:
        courses = []

    course_id = topic.course_id
    course_completion = CourseCompletion.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    total_tasks = Element.query.join(Topic).filter(Topic.course_id == course_id,
                                                   Element.element_type == 'Задание').count()
    if course_completion is not None:
        completed_tasks = course_completion.points
    else:
        completed_tasks = 0  # или любое другое значение по умолчанию
    plot = create_plot(course_id)
    plot1 = create_plot1(course_id)

    return render_template('Course.html', course=course, institutions=institutions, authors=authors,
                           students=students, author_details=author_details, plot=plot, plot1=plot1,
                           form=form, edit_mode=edit_mode, topics=topics, groups=groups, course_code=course_code, courses=courses, role=current_user.role,
                           student_groups=student_groups, messages=messages, group_id=group_id, course_completion=course_completion,completed_tasks = completed_tasks, total_tasks =total_tasks)



#_______________________________________________________________________________
#ЗАПУСКкк

if __name__ == '__main__':
    app.run(app.run( debug=True))
    asyncio.run(main())
