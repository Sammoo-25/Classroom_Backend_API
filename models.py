from flask_login import UserMixin
from flask_security import RoleMixin
from app import db
from helpers import generate_hash
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    create_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))
    progresses = db.relationship('Progress', cascade="all,delete", backref='user', lazy='dynamic')
    full_progresses = db.relationship('FullProgress', cascade="all,delete", backref='user', lazy='dynamic')
    exams = db.relationship('Exam', cascade="all,delete", backref='User', lazy='dynamic')
    exam_due_dates = db.relationship('ExamDueDates', cascade="all,delete", backref='User', lazy='dynamic')
    mentor_of_course = db.relationship('MentorOfCourse', cascade="all,delete", backref='User', lazy='dynamic')

    def user_to_dict(self):
        user_dict = {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'birthday': self.birthday,
            'create': self.create_date
        }
        return user_dict


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)


class UserRoles(db.Model, RoleMixin):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('role.id'))


class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    progress_value = db.Column(db.Integer, nullable=False, default=0)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # TODO write table name
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # TODO write table name


class FullProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress_value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)  # TODO progress reference, topic reference
    progresses = db.relationship('Progress', backref='course', lazy='dynamic')
    topics = db.relationship('Topic', cascade="all,delete", backref='course', lazy='dynamic')
    exams = db.relationship('Exam', cascade="all,delete", backref='Course', lazy='dynamic')
    exam_due_dates = db.relationship('ExamDueDates', cascade="all,delete", backref='Course', lazy='dynamic')
    mentor_of_course = db.relationship('MentorOfCourse', cascade="all,delete", backref='Course', lazy='dynamic')


    def course_to_dict(self):
        return {'id':self.id, 'course_name':self.course_name}


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), nullable=False, unique=True)
    training_courses = db.relationship('TrainingCourses', cascade="all,delete", backref='team', lazy='dynamic')
    team_lead_of_teams = db.relationship('TeamLeadOfTeam', cascade="all,delete", backref='team', lazy='dynamic')

    def team_to_dict(self):
        return {'id': self.id, 'team_name': self.team_name}


class TrainingCourses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    training_queue = db.Column(db.Integer, unique=True, nullable=False)


class TeamLeadOfTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class MentorOfCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # TODO subtopic reference
    topic_queue = db.Column(db.Integer, nullable=False)
    subtopics = db.relationship('Subtopic', cascade="all,delete", backref='topic', lazy='dynamic')
    source_of_learning = db.relationship('SourceOfLearningTextContent', cascade="all,delete", backref='topic',
                                         lazy='dynamic')
    source_of_learning_video_content = db.relationship('SourceOfLearningVideoContent', cascade="all,delete",
                                                       backref='topic', lazy='dynamic')


class Subtopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtopic_name = db.Column(db.String(255), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    subtopic_queue = db.Column(db.Integer, nullable=False)
    questions = db.relationship('Question', cascade="all,delete", backref='subtopic', lazy='dynamic')
    exercises = db.relationship('Exercise', cascade="all,delete", backref='subtopic', lazy='dynamic')
    subtopicgroups = db.relationship('SubTopicGroup', cascade="all,delete", backref='subtopic', lazy='dynamic')
    source_of_learning = db.relationship('SourceOfLearningTextContent', cascade="all,delete", backref='subtopic',
                                         lazy='dynamic')
    source_of_learning_video_content = db.relationship('SourceOfLearningVideoContent', cascade="all,delete",
                                                       backref='subtopic', lazy='dynamic')


class SourceOfLearningTextContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_content_header = db.Column(db.String(255), nullable=False)
    source_content_plain_text = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=True)


class SourceOfLearningVideoContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(255), nullable=False)
    video_path = db.Column(db.String(255), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=True)
    video_queue = db.Column(db.Integer, nullable=False)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(50), nullable=False)
    subtopicgroups = db.relationship('SubTopicGroup', cascade="all,delete", backref='group', lazy='dynamic')


class SubTopicGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_context = db.Column(db.Text, nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    trueanswers = db.relationship('TrueAnswer', cascade="all,delete", backref='question', lazy='dynamic')
    falseanswers = db.relationship('FalseAnswer', cascade="all,delete", backref='question', lazy='dynamic')


class TrueAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_context = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)  # TODO


class FalseAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_context = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)  # TODO


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_context = db.Column(db.Text, nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)  # TODO


class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    pdf_link = db.Column(db.String(255), nullable=False)
    exams = db.relationship('Exam', cascade="all,delete", backref='ExamResult', lazy='dynamic')


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_result_id = db.Column(db.Integer, db.ForeignKey('exam_result.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class ExamDueDates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_expected_date = db.Column(db.Date, nullable=False)
