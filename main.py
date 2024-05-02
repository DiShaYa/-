from flask import Flask, render_template, request, url_for, session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_uploads import UploadSet, IMAGES, configure_uploads, DOCUMENTS

app = Flask(__name__)

# Настройки базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '555a89580ca293c1076e8dbd2aa7786b71b528cc'


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)


#_______________________________________________________________________________
#БАЗА ДАННЫХ

class Tests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))

class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    is_correct = db.Column(db.Boolean)

#_____________________________ новые таблицы

user_institutions = db.Table('user_institutions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('institution_id', db.Integer, db.ForeignKey('institutions.id'))
)

class User(db.Model, UserMixin):
     __tablename__ = 'users'
     id = db.Column(db.Integer, primary_key=True)
     login = db.Column(db.Char, nullable=False, unique = True)
     password = db.Column(db.Char, nullable=False)
     mail = db.Column(db.Char, nullable = True, unique = True)
     name = db.Column(db.Char, nullable=False) #офиц имя
     status = db.Column(db.Char, nullable=False) #статус пользователя: права
     created_at = db.Column(db.DateTime, default=datetime.utcnow) #время создания пользователя

     institutions = db.relationship('Institution', secondary=user_institutions, backref='users')#заведения


courses_institutions = db.Table('courses_institutions',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('institution_id', db.Integer, db.ForeignKey('institutions.id'))
)


class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, default='название заведения') #название заведения
    type = db.Column(db.String, nullable=True, default='тип заведения') #тип заведения: предприятие, университет, бизнес  и тд. свободная форма

    courses = db.relationship('Course', secondary=courses_institutions, backref='institutions')

course_authors = db.Table('course_authors',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('users.id'))
)

class Сourse(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, default='название курса')
    description = db.Column(db.String, nullable=True)
    equipments = db.Column(db.String, nullable=True)
    language = db.Column(db.String, nullable=True)
    difficulty = db.Column(db.String, nullable=True)
    duration = db.Column(db.String, nullable=True)
    initial_requirements = db.Column(db.String, nullable=True)

    authors = db.relationship('User', secondary=course_authors, backref='courses')


class CourseCompletion(db.Model):
    __tablename__ = 'course_completions'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    completion_status = db.Column(db.String, default='False')
    points = db.Column(db.Integer, default = 0)
    grade = db.Column(db.String, nullable=True)

class Topic(db.Model): #Темы
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False , default='название темы')
    index = db.Column(db.Integer, nullable=False) #порядок отображения

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)


#_______________________________________________________________________________

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# # Пример для добавления тестов
# with app.app_context():
#     test1 = Tests(name='Тест 1')
#     db.session.add(test1)
#
#     # Пример для добавления вопросов
#     question1 = Questions(text='Что такое программирование?', test_id=test1.id)
#     question2 = Questions(text='Сколько битов в байте?', test_id=test1.id)
#     question3 = Questions(text='Каой язык программирования интерпретируемый?', test_id=test1.id)
#     db.session.add(question1)
#     db.session.add(question2)
#     db.session.add(question3)
#
#     # Пример для добавления ответов
#     answer1 = Answers(text='Тестирование приложения', question_id=question1.id, is_correct=False)
#     answer2 = Answers(text='Создание программ с помощью написания кода', question_id=question1.id, is_correct=True)
#
#     answer3 = Answers(text='Python', question_id=question3.id, is_correct=True)
#     answer4 = Answers(text='Pasqal', question_id=question3.id, is_correct=False)
#     answer5 = Answers(text='Java', question_id=question3.id, is_correct=False)
#     db.session.add(answer3)
#     db.session.add(answer4)
#     db.session.add(answer5)
#
#     db.session.add(answer1)
#     db.session.add(answer2)
#
#     # Фиксируем изменения в базе данных
#     db.session.commit()


#_______________________________________________________________________________
#МАРШРУТИЗАТОРЫ

@app.route('/')
def mainpage():
    return render_template('mainpage.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/uploadlecture')
def uploadlecture():
    return render_template('uploadlecture.html')

@app.route('/createtest')
def createtest():
    tests = Tests.query.all()
    test_data = []

    for test in tests:
        test_item = {
            'test_id': test.id,
            'test_name': test.name,
            'questions': []
        }
        questions = Questions.query.filter_by(test_id=test.id).all()

        for question in questions:
            question_item = {
                'question_text': question.text,
                'answers': []
            }
            answers = Answers.query.all()

            for answer in answers:
                answer_item = {
                    'answer_text': answer.text
                }
                question_item['answers'].append(answer_item)

            test_item['questions'].append(question_item)

        test_data.append(test_item)

    return render_template('createtest.html', test_data=test_data)


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
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        pass
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    pass

@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    pass


#_______________________________________________________________________________
#ЗАПУСК

if __name__ == '__main__':
    app.run(app.run( debug=True))
