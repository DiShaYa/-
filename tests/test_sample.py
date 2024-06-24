import pytest
from main import app, db
from main import  User, Institution, Course, CourseCompletion, Topic, Task, Lecture, Answer, Test, Element, ChatMessenger, GroupMembership, Group



@pytest.fixture
def app_context():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


def test_user_creation(app_context):
    with app_context.app_context():
        user = User(
            login='testuser',
            password='password',
            mail='test@example.com',
            name='Test User',
            role='Преподователь'
        )
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(mail='test@example.com').first()
        assert saved_user is not None
        assert saved_user.name == 'Test User'
        assert saved_user.role == 'Преподователь'

def test_user_update(app_context):
    with app_context.app_context():
        # Создаем и сохраняем пользователя
        user = User(
            login='testuser',
            password='password',
            mail='test@example.com',
            name='Test User',
            role='Преподователь'
        )
        db.session.add(user)
        db.session.commit()

        # Обновляем данные пользователя
        user.name = 'Updated Test User'
        user.role = 'Студент'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_user = User.query.filter_by(mail='test@example.com').first()
        assert updated_user is not None
        assert updated_user.name == 'Updated Test User'
        assert updated_user.role == 'Студент'

def test_user_deletion(app_context):
    with app_context.app_context():
        # Создаем и сохраняем пользователя
        user = User(
            login='testuser',
            password='password',
            mail='test@example.com',
            name='Test User',
            role='Преподователь'
        )
        db.session.add(user)
        db.session.commit()

        # Удаляем пользователя
        db.session.delete(user)
        db.session.commit()

        # Проверяем, что пользователь успешно удален из базы данных
        deleted_user = User.query.filter_by(mail='test@example.com').first()
        assert deleted_user is None

def test_institution_creation(app_context):
    with app_context.app_context():
        institution = Institution(name='Test Institution', type='University')
        db.session.add(institution)
        db.session.commit()

        saved_institution = Institution.query.filter_by(name='Test Institution').first()
        assert saved_institution is not None
        assert saved_institution.type == 'University'
def test_institution_update(app_context):
    with app_context.app_context():
        # Создаем и сохраняем учреждение
        institution = Institution(name='Test Institution', type='University')
        db.session.add(institution)
        db.session.commit()

        # Обновляем данные учреждения
        institution.name = 'Updated Test Institution'
        institution.type = 'College'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_institution = Institution.query.filter_by(name='Updated Test Institution').first()
        assert updated_institution is not None
        assert updated_institution.type == 'College'

def test_institution_deletion(app_context):
    with app_context.app_context():
        # Создаем и сохраняем учреждение
        institution = Institution(name='Test Institution', type='University')
        db.session.add(institution)
        db.session.commit()

        # Удаляем учреждение
        db.session.delete(institution)
        db.session.commit()

        # Проверяем, что учреждение успешно удалено из базы данных
        deleted_institution = Institution.query.filter_by(name='Test Institution').first()
        assert deleted_institution is None
def test_course_creation(app_context):
    with app_context.app_context():
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        saved_course = Course.query.filter_by(name='Test Course').first()
        assert saved_course is not None
        assert saved_course.description == 'Description of test course'
def test_course_update(app_context):
    with app_context.app_context():
        # Создаем и сохраняем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Обновляем данные курса
        course.name = 'Updated Test Course'
        course.description = 'Updated description'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_course = Course.query.filter_by(name='Updated Test Course').first()
        assert updated_course is not None
        assert updated_course.description == 'Updated description'

def test_course_deletion(app_context):
    with app_context.app_context():
        # Создаем и сохраняем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Удаляем курс
        db.session.delete(course)
        db.session.commit()

        # Проверяем, что курс успешно удален из базы данных
        deleted_course = Course.query.filter_by(name='Test Course').first()
        assert deleted_course is None
def test_course_completion_creation(app_context):
    with app_context.app_context():
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        saved_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert saved_completion is not None
        assert saved_completion.completion_status == 'True'
        assert saved_completion.points == 100
        assert saved_completion.grade == 'A'

def test_course_completion_update(app_context):
    with app_context.app_context():
        # Создаем пользователя и курс
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем и сохраняем завершение курса
        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        # Обновляем данные завершения курса
        course_completion.completion_status = 'False'
        course_completion.points = 50
        course_completion.grade = 'B'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert updated_completion is not None
        assert updated_completion.completion_status == 'False'
        assert updated_completion.points == 50
        assert updated_completion.grade == 'B'

def test_course_completion_deletion(app_context):
    with app_context.app_context():
        # Создаем пользователя и курс
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем и сохраняем завершение курса
        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        # Удаляем завершение курса
        db.session.delete(course_completion)
        db.session.commit()

        # Проверяем, что завершение курса успешно удалено из базы данных
        deleted_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert deleted_completion is None

def test_topic_creation(app_context):
    with app_context.app_context():
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        topic = Topic(name='Test Topic', index=1, course_id=course.id)
        db.session.add(topic)
        db.session.commit()

        saved_topic = Topic.query.filter_by(name='Test Topic').first()
        assert saved_topic is not None
        assert saved_topic.index == 1
        assert saved_topic.course_id == course.id

def test_topic_update(app_context):
    with app_context.app_context():
        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем и сохраняем тему
        topic = Topic(name='Test Topic', index=1, course_id=course.id)
        db.session.add(topic)
        db.session.commit()

        # Обновляем данные темы
        topic.name = 'Updated Test Topic'
        topic.index = 2
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_topic = Topic.query.filter_by(name='Updated Test Topic').first()
        assert updated_topic is not None
        assert updated_topic.index == 2

def test_topic_deletion(app_context):
    with app_context.app_context():
        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем и сохраняем тему
        topic = Topic(name='Test Topic', index=1, course_id=course.id)
        db.session.add(topic)
        db.session.commit()

        # Удаляем тему
        db.session.delete(topic)
        db.session.commit()

        # Проверяем, что тема успешно удалена из базы данных
        deleted_topic = Topic.query.filter_by(name='Test Topic').first()
        assert deleted_topic is None
def test_task_creation(app_context):
    with app_context.app_context():
        task = Task(question='Test question for task')
        db.session.add(task)
        db.session.commit()

        saved_task = Task.query.filter_by(question='Test question for task').first()
        assert saved_task is not None

def test_task_update(app_context):
    with app_context.app_context():
        # Создаем задание
        task = Task(question='Test question for task')
        db.session.add(task)
        db.session.commit()

        # Обновляем данные задания
        task.question = 'Updated test question for task'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_task = Task.query.filter_by(question='Updated test question for task').first()
        assert updated_task is not None

def test_task_deletion(app_context):
    with app_context.app_context():
        # Создаем задание
        task = Task(question='Test question for task')
        db.session.add(task)
        db.session.commit()

        # Удаляем задание
        db.session.delete(task)
        db.session.commit()

        # Проверяем, что задание успешно удалено из базы данных
        deleted_task = Task.query.filter_by(question='Test question for task').first()
        assert deleted_task is None
def test_lecture_creation(app_context):
    with app_context.app_context():
        lecture = Lecture(title='Test Lecture', description='Description of test lecture')
        db.session.add(lecture)
        db.session.commit()

        saved_lecture = Lecture.query.filter_by(title='Test Lecture').first()
        assert saved_lecture is not None
        assert saved_lecture.description == 'Description of test lecture'
def test_lecture_update(app_context):
    with app_context.app_context():
        # Создаем лекцию
        lecture = Lecture(title='Test Lecture', description='Description of test lecture')
        db.session.add(lecture)
        db.session.commit()

        # Обновляем данные лекции
        lecture.title = 'Updated Test Lecture'
        lecture.description = 'Updated description of test lecture'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_lecture = Lecture.query.filter_by(title='Updated Test Lecture').first()
        assert updated_lecture is not None
        assert updated_lecture.description == 'Updated description of test lecture'

def test_lecture_deletion(app_context):
    with app_context.app_context():
        # Создаем лекцию
        lecture = Lecture(title='Test Lecture', description='Description of test lecture')
        db.session.add(lecture)
        db.session.commit()

        # Удаляем лекцию
        db.session.delete(lecture)
        db.session.commit()

        # Проверяем, что лекция успешно удалена из базы данных
        deleted_lecture = Lecture.query.filter_by(title='Test Lecture').first()
        assert deleted_lecture is None
def test_answer_creation(app_context):
    with app_context.app_context():
        task = Task(question='Test question for answer')
        db.session.add(task)
        db.session.commit()

        answer = Answer(correct_answer='Test correct answer', task_id=task.id)
        db.session.add(answer)
        db.session.commit()

        saved_answer = Answer.query.filter_by(correct_answer='Test correct answer').first()
        assert saved_answer is not None
        assert saved_answer.task_id == task.id
def test_answer_update(app_context):
    with app_context.app_context():
        # Создаем задание и ответ
        task = Task(question='Test question for answer')
        db.session.add(task)
        db.session.commit()

        answer = Answer(correct_answer='Test correct answer', task_id=task.id)
        db.session.add(answer)
        db.session.commit()

        # Обновляем данные ответа
        answer.correct_answer = 'Updated test correct answer'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_answer = Answer.query.filter_by(correct_answer='Updated test correct answer').first()
        assert updated_answer is not None

def test_answer_deletion(app_context):
    with app_context.app_context():
        # Создаем задание и ответ
        task = Task(question='Test question for answer')
        db.session.add(task)
        db.session.commit()

        answer = Answer(correct_answer='Test correct answer', task_id=task.id)
        db.session.add(answer)
        db.session.commit()

        # Удаляем ответ
        db.session.delete(answer)
        db.session.commit()

        # Проверяем, что ответ успешно удален из базы данных
        deleted_answer = Answer.query.filter_by(correct_answer='Test correct answer').first()
        assert deleted_answer is None
def test_test_creation(app_context):
    with app_context.app_context():
        task = Task(question='Test question for test')
        db.session.add(task)
        db.session.commit()

        test = Test(option1='Option 1', option2='Option 2', option3='Option 3', option4='Option 4', correct_option=1, task_id=task.id)
        db.session.add(test)
        db.session.commit()

        saved_test = Test.query.filter_by(option1='Option 1').first()
        assert saved_test is not None
        assert saved_test.task_id == task.id
def test_test_update(app_context):
    with app_context.app_context():
        # Создаем задание и тест
        task = Task(question='Test question for test')
        db.session.add(task)
        db.session.commit()

        test = Test(option1='Option 1', option2='Option 2', option3='Option 3', option4='Option 4', correct_option=1, task_id=task.id)
        db.session.add(test)
        db.session.commit()

        # Обновляем данные теста
        test.option1 = 'Updated Option 1'
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_test = Test.query.filter_by(option1='Updated Option 1').first()
        assert updated_test is not None

def test_test_deletion(app_context):
    with app_context.app_context():
        # Создаем задание и тест
        task = Task(question='Test question for test')
        db.session.add(task)
        db.session.commit()

        test = Test(option1='Option 1', option2='Option 2', option3='Option 3', option4='Option 4', correct_option=1, task_id=task.id)
        db.session.add(test)
        db.session.commit()

        # Удаляем тест
        db.session.delete(test)
        db.session.commit()

        # Проверяем, что тест успешно удален из базы данных
        deleted_test = Test.query.filter_by(option1='Option 1').first()
        assert deleted_test is None
def test_element_creation(app_context):
    with app_context.app_context():
        topic = Topic(name='Test Topic', index=1)
        db.session.add(topic)
        db.session.commit()

        element_lecture = Element(element_type='Лекция', element_id=1, topic_id=topic.id)
        db.session.add(element_lecture)
        db.session.commit()

        saved_lecture_element = Element.query.filter_by(element_type='Лекция').first()
        assert saved_lecture_element is not None
        assert saved_lecture_element.topic_id == topic.id
def test_element_update(app_context):
    with app_context.app_context():
        # Создаем тему и элемент лекции
        topic = Topic(name='Test Topic', index=1)
        db.session.add(topic)
        db.session.commit()

        element_lecture = Element(element_type='Лекция', element_id=1, topic_id=topic.id)
        db.session.add(element_lecture)
        db.session.commit()

        # Обновляем данные элемента лекции
        element_lecture.element_id = 2
        db.session.commit()

        # Проверяем, что данные обновлены корректно
        updated_element = Element.query.filter_by(element_type='Лекция').first()
        assert updated_element is not None
        assert updated_element.element_id == 2

def test_element_deletion(app_context):
    with app_context.app_context():
        # Создаем тему и элемент лекции
        topic = Topic(name='Test Topic', index=1)
        db.session.add(topic)
        db.session.commit()

        element_lecture = Element(element_type='Лекция', element_id=1, topic_id=topic.id)
        db.session.add(element_lecture)
        db.session.commit()

        # Удаляем элемент лекции
        db.session.delete(element_lecture)
        db.session.commit()

        # Проверяем, что элемент лекции успешно удален из базы данных
        deleted_element = Element.query.filter_by(element_type='Лекция').first()
        assert deleted_element is None

def test_chat_messenger_creation(app_context):
    with app_context.app_context():
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        chat_message = ChatMessenger(message='Test message', user_id=user.id, course_id=course.id)
        db.session.add(chat_message)
        db.session.commit()

        saved_message = ChatMessenger.query.filter_by(message='Test message').first()
        assert saved_message is not None
        assert str(saved_message.user_id) == str(user.id)
        assert str(saved_message.course_id) == str(course.id)
def test_chat_messenger_update(app_context):
    with app_context.app_context():
        # Создаем пользователя и курс
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем сообщение чата
        chat_message = ChatMessenger(message='Test message', user_id=user.id, course_id=course.id)
        db.session.add(chat_message)
        db.session.commit()

        # Обновляем сообщение чата
        chat_message.message = 'Updated test message'
        db.session.commit()

        # Проверяем, что сообщение чата было успешно обновлено
        updated_message = ChatMessenger.query.filter_by(message='Updated test message').first()
        assert updated_message is not None

def test_chat_messenger_deletion(app_context):
    with app_context.app_context():
        # Создаем пользователя и курс
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем сообщение чата
        chat_message = ChatMessenger(message='Test message', user_id=user.id, course_id=course.id)
        db.session.add(chat_message)
        db.session.commit()

        # Удаляем сообщение чата
        db.session.delete(chat_message)
        db.session.commit()

        # Проверяем, что сообщение чата успешно удалено из базы данных
        deleted_message = ChatMessenger.query.filter_by(message='Test message').first()
        assert deleted_message is None

def test_group_membership_creation(app_context):
    with app_context.app_context():
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        group = Group(name='Test Group')
        db.session.add(group)
        db.session.commit()

        group_membership = GroupMembership(user_id=user.id, group_id=group.id)
        db.session.add(group_membership)
        db.session.commit()

        saved_membership = GroupMembership.query.filter_by(user_id=user.id, group_id=group.id).first()
        assert saved_membership is not None
def test_group_membership_update(app_context):
    with app_context.app_context():
        # Создаем пользователя и группу
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        group = Group(name='Test Group')
        db.session.add(group)
        db.session.commit()

        # Создаем членство в группе
        group_membership = GroupMembership(user_id=user.id, group_id=group.id)
        db.session.add(group_membership)
        db.session.commit()

        # Обновляем членство в группе
        group_membership.group_id = 2  # Изменяем идентификатор группы
        db.session.commit()

        # Проверяем, что членство в группе было успешно обновлено
        updated_membership = GroupMembership.query.filter_by(user_id=user.id, group_id=2).first()
        assert updated_membership is not None

def test_group_membership_deletion(app_context):
    with app_context.app_context():
        # Создаем пользователя и группу
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        group = Group(name='Test Group')
        db.session.add(group)
        db.session.commit()

        # Создаем членство в группе
        group_membership = GroupMembership(user_id=user.id, group_id=group.id)
        db.session.add(group_membership)
        db.session.commit()

        # Удаляем членство в группе
        db.session.delete(group_membership)
        db.session.commit()

        # Проверяем, что членство в группе успешно удалено из базы данных
        deleted_membership = GroupMembership.query.filter_by(user_id=user.id, group_id=group.id).first()
        assert deleted_membership is None
def test_group_creation(app_context):
    with app_context.app_context():
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        group = Group(name='Test Group', course_id=course.id)
        db.session.add(group)
        db.session.commit()

        saved_group = Group.query.filter_by(name='Test Group').first()
        assert saved_group is not None
        assert saved_group.course_id == course.id
def test_group_update(app_context):
    with app_context.app_context():
        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем группу
        group = Group(name='Test Group', course_id=course.id)
        db.session.add(group)
        db.session.commit()

        # Обновляем данные группы
        group.name = 'Updated Test Group'
        db.session.commit()

        # Проверяем, что данные группы были успешно обновлены
        updated_group = Group.query.filter_by(name='Updated Test Group').first()
        assert updated_group is not None

def test_group_deletion(app_context):
    with app_context.app_context():
        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем группу
        group = Group(name='Test Group', course_id=course.id)
        db.session.add(group)
        db.session.commit()

        # Удаляем группу
        db.session.delete(group)
        db.session.commit()

        # Проверяем, что группа успешно удалена из базы данных
        deleted_group = Group.query.filter_by(name='Test Group').first()
        assert deleted_group is None

def test_course_completion_creation(app_context):
    with app_context.app_context():
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        saved_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert saved_completion is not None
        assert saved_completion.completion_status == 'True'
        assert saved_completion.points == 100
        assert saved_completion.grade == 'A'

def test_course_completion_update(app_context):
    with app_context.app_context():
        # Создаем пользователя
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем завершение курса
        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        # Обновляем данные завершения курса
        course_completion.completion_status = 'False'
        course_completion.points = 50
        course_completion.grade = 'B'
        db.session.commit()

        # Проверяем, что данные завершения курса были успешно обновлены
        updated_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert updated_completion is not None
        assert updated_completion.completion_status == 'False'
        assert updated_completion.points == 50
        assert updated_completion.grade == 'B'

def test_course_completion_deletion(app_context):
    with app_context.app_context():
        # Создаем пользователя
        user = User(login='testuser', password='password', mail='test@example.com', name='Test User', role='Преподователь')
        db.session.add(user)
        db.session.commit()

        # Создаем курс
        course = Course(name='Test Course', description='Description of test course')
        db.session.add(course)
        db.session.commit()

        # Создаем завершение курса
        course_completion = CourseCompletion(user_id=user.id, course_id=course.id, completion_status='True', points=100, grade='A')
        db.session.add(course_completion)
        db.session.commit()

        # Удаляем завершение курса
        db.session.delete(course_completion)
        db.session.commit()

        # Проверяем, что завершение курса успешно удалено из базы данных
        deleted_completion = CourseCompletion.query.filter_by(user_id=user.id, course_id=course.id).first()
        assert deleted_completion is None