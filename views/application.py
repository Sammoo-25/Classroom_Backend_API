import os

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required
from flask_login import logout_user, current_user
from werkzeug.utils import secure_filename

from app import app, db, login_manager
from helpers import generate_hash, quick_sort, save_file
from models import User, Course, FullProgress, Team, Role, UserRoles, TeamLeadOfTeam, MentorOfCourse, \
    TrainingCourses, Topic, Subtopic, SourceOfLearningTextContent, SourceOfLearningVideoContent


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#
# @app.route('/')
# def index():
#     form = LoginForm()
#     return render_template('application/loginform/index.html', form=form)

# ---Samo---#
@app.route('/login', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username, password=generate_hash(password)).first()
        if user:
            user_role = UserRoles.query.filter_by(user_id=user.id).first()
            role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
            if data['username'] == user.username and generate_hash(data['password']) == user.password:
                if role_name == 'mentor':
                    access_token = create_access_token(identity=username)
                    return jsonify(access_token=access_token), 200
                elif role_name == 'teamlead':
                    access_token = create_access_token(identity=username)
                    return jsonify(access_token=access_token), 200
                elif role_name == 'student':
                    access_token = create_access_token(identity=username)
                    return jsonify(access_token=access_token), 200
                else:
                    return jsonify(message='Invalid username or password'), 401
        return jsonify(message='Method Not Allowed'), 405


@app.route('/get_courses/<mentor_username>', methods=['GET'])
@jwt_required()
def get_mentor_courses(mentor_username):
    if request.method == 'GET':
        mentor_courses = (
            db.session.query(Course)
            .join(MentorOfCourse, MentorOfCourse.course_id == Course.id)
            .join(User, User.id == MentorOfCourse.user_id)
            .filter(User.username == mentor_username)
            .all()
        )

        courses_data = [
            {
                'course_name': course.course_name,
                'course_id': course.id
            }
            for course in mentor_courses
        ]

        return jsonify({'mentor_courses': courses_data}), 200
    return jsonify({'error': 'An error occurred while fetching mentor courses'}), 500


# ---Samo---#

# @app.route('/get_students_by_courses', methods=['POST'])
# def get_students_by_courses():
#     data = request.json
#     course_ids_list = data.get('course_ids')
#     students_list = []


@app.route('/add_topic/<course>', methods=['POST'])
def add_topic(course):
    if request.method == 'POST':
        data = request.json
        topic_name = data['topic']
        course_obj = Course.query.filter_by(course_name=course).first()

        if course_obj:
            topic_count = Topic.query.filter_by(course_id=course_obj.id).count()

            new_topic = Topic(
                topic_name=topic_name,
                course_id=course_obj.id,
                topic_queue=topic_count + 1
            )
            db.session.add(new_topic)
            db.session.commit()
            return jsonify({'message': 'Successfully added'}), 200
    return jsonify({'error': 'An error occurred while adding the topic'}), 500


@app.route('/edit_topic/<course>/<topic_id>', methods=['PUT'])
def edit_topic(course, topic_id):
    data = request.json
    if request.method == 'PUT':
        courses = Course.query.filter_by(course_name=course).first()
        course_topices = Topic.query.filter_by(course_id=courses.id, id=topic_id).first()
        topic_new_name = data.get('new_name')
        course_topices.topic_name = topic_new_name
        db.session.commit()
        return jsonify({'message': 'Topic edited successfully'}), 200
    else:
        jsonify(message='bad request'), 400

    return jsonify(message='bad request'), 400


@app.route('/delete_topic/<course>/<topic_id>', methods=['DELETE'])
def delete_topic(course, topic_id):
    if request.method == 'DELETE':
        courses = Course.query.filter_by(course_name=course).first()
        course_topics = Topic.query.filter_by(course_id=courses.id, id=topic_id).first()
        if course_topics:
            db.session.delete(course_topics)
            db.session.commit()
            return jsonify({'message': 'Topic deleted successfully'}), 200
    return jsonify(message='bad request'), 400


@app.route('/get_topic_by_cource/<course_name>', methods=['GET'])
def get_topic_by_cource(course_name):
    if request.method == 'GET':
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            course_topics = Topic.query.filter_by(course_id=course.id).all()
            topics = []

            for topic in course_topics:
                topic_data = {
                    "id": topic.id,
                    "topic": topic.topic_name,
                    "queue": topic.topic_queue
                }
                topics.append(topic_data)

            data = {
                "course": course_name,
                "topics": topics
            }
            return jsonify(data), 200

        return jsonify({"message": "Course not found"}), 404

    return jsonify({"message": "Bad request"}), 400


@app.route('/add/video_to_topic/<course>', methods=['POST'])
def add_video_to_topic(course):
    if request.method == "POST":
        data = request.json
        video_path = data.get('video_path')
        video_name = data.get('video_name')
        course_object = Course.query.filter_by(course_name=course).first()

        if course_object:
            selected_topic = Topic.query.filter_by(course_id=course_object.id, id=data.get('topic_id')).first()

            if selected_topic:
                # selected_subtopic = Subtopic.query.filter_by(topic_id=selected_topic.id).first()

                # if selected_subtopic:
                video_count = SourceOfLearningVideoContent.query.filter_by(topic_id=selected_topic.id,
                                                                           subtopic=None).count()
                new_video_content = SourceOfLearningVideoContent(
                    video_name=video_name,
                    video_path=video_path,
                    topic_id=selected_topic.id,
                    # subtopic_id=selected_subtopic.id,
                    video_queue=video_count + 1
                )
                db.session.add(new_video_content)
                db.session.commit()
                return jsonify({'message': 'Video Successfully added for topic'}), 200

    return jsonify({'error': 'An error occurred while adding the video'}), 500


@app.route('/add/content_to_topic/<course>', methods=['POST'])
def add_content_to_topic(course):
    if request.method == "POST":
        data = request.json
        source_content_header = data.get('source_content_header')
        source_content_plain_text = data.get('source_content_plain_text')
        course_object = Course.query.filter_by(course_name=course).first()

        if course_object:
            selected_topic = Topic.query.filter_by(course_id=course_object.id, id=data.get('topic_id')).first()

            if selected_topic:
                # selected_subtopic = Subtopic.query.filter_by(topic_id=selected_topic.id).first()

                # if selected_subtopic:
                new_text_content = SourceOfLearningTextContent(
                    source_content_header=source_content_header,
                    source_content_plain_text=source_content_plain_text,
                    topic_id=selected_topic.id,
                    # subtopic_id=selected_subtopic.id,
                )
                db.session.add(new_text_content)
                db.session.commit()
                return jsonify({'content_id': new_text_content.id}), 200

    return jsonify({'error': 'An error occurred while adding the content'}), 500


@app.route('/get_source_by_topic/<topic>', methods=['GET'])
def get_source_by_topic(topic):
    if request.method == 'GET':
        topic_obj = Topic.query.filter_by(topic_name=topic).first()

        if topic_obj:
            response_data = {
                "source": [],
                "topic": topic_obj.topic_name

            }

            video_content_list = SourceOfLearningVideoContent.query.filter_by(topic_id=topic_obj.id,
                                                                              subtopic_id=None).all()

            text_content_list = SourceOfLearningTextContent.query.filter_by(topic_id=topic_obj.id,
                                                                            subtopic_id=None).all()

            for video_content in video_content_list:
                video_data = {
                    "id": video_content.id,
                    "source_video_path": video_content.video_path,
                    "video_name": video_content.video_name
                }
                response_data["source"].append(video_data)

            for text_content in text_content_list:
                text_data = {
                    "id": text_content.id,
                    "source_content_header": text_content.source_content_header,
                    "source_content": text_content.source_content_plain_text,
                }
                response_data["source"].append(text_data)

            return jsonify(response_data), 200

    return jsonify({'message': 'Topic not found'}), 404


@app.route('/add/video_to_subtopic/<course>', methods=['POST'])
def add_video_to_subtopic(course):
    if request.method == "POST":
        data = request.json
        video_path = data.get('video_path')
        video_name = data.get('video_name')
        course_object = Course.query.filter_by(course_name=course).first()

        if course_object:
            selected_topic = Topic.query.filter_by(course_id=course_object.id, id=data.get('topic_id')).first()

            if selected_topic:
                selected_subtopic = Subtopic.query.filter_by(topic_id=selected_topic.id).first()

                if selected_subtopic:
                    video_count = SourceOfLearningVideoContent.query.filter(
                        SourceOfLearningVideoContent.topic_id == selected_topic.id,
                        SourceOfLearningVideoContent.subtopic_id.isnot(None)
                    ).count()
                    new_video_content = SourceOfLearningVideoContent(
                        video_name=video_name,
                        video_path=video_path,
                        topic_id=selected_topic.id,
                        subtopic_id=selected_subtopic.id,
                        video_queue=video_count + 1
                    )
                    db.session.add(new_video_content)
                    db.session.commit()
                    return jsonify({'message': 'Video Successfully added '}), 200

    return jsonify({'error': 'An error occurred while adding the video'}), 500


@app.route('/add/content_to_subtopic/<course>', methods=['POST'])
def add_content_to_subtopic(course):
    if request.method == "POST":
        data = request.json
        source_content_header = data.get('source_content_header')
        source_content_plain_text = data.get('source_content_plain_text')
        course_object = Course.query.filter_by(course_name=course).first()

        if course_object:
            selected_topic = Topic.query.filter_by(course_id=course_object.id, id=data.get('topic_id')).first()

            if selected_topic:
                selected_subtopic = Subtopic.query.filter_by(topic_id=selected_topic.id).first()

                if selected_subtopic:
                    new_text_content = SourceOfLearningTextContent(
                        source_content_header=source_content_header,
                        source_content_plain_text=source_content_plain_text,
                        topic_id=selected_topic.id,
                        subtopic_id=selected_subtopic.id,
                    )
                    db.session.add(new_text_content)
                    db.session.commit()
                    return jsonify({'content_id': new_text_content.id}), 200

    return jsonify({'error': 'An error occurred while adding the content'}), 500


@app.route('/get_source_by_subtopic/<subtopic_name>', methods=['GET'])
def get_source_by_subtopic(subtopic_name):
    if request.method == 'GET':
        subtopic_obj = Subtopic.query.filter_by(subtopic_name=subtopic_name).first()

        if subtopic_obj:
            response_data = {
                "source": [],
                "subtopic": subtopic_obj.subtopic_name
            }
            video_content_list = SourceOfLearningVideoContent.query.filter_by(subtopic_id=subtopic_obj.id).all()

            text_content_list = SourceOfLearningTextContent.query.filter_by(subtopic_id=subtopic_obj.id).all()

            for subtopic_video_content in video_content_list:
                video_data = {
                    "id": subtopic_video_content.id,
                    "source_video_path": subtopic_video_content.video_path,
                    "video_name": subtopic_video_content.video_name
                }
                response_data["source"].append(video_data)

            for subtopic_text_content in text_content_list:
                text_data = {
                    "id": subtopic_text_content.id,
                    "source_content_header": subtopic_text_content.source_content_header,
                    "source_content": subtopic_text_content.source_content_plain_text,
                }
                response_data["source"].append(text_data)

            return jsonify(response_data), 200


    return jsonify({'message': 'Topic not found'}), 404


# --------SUBTOPIC--------#
@app.route('/add_subtopic/<course>', methods=['POST'])
def add_subtopic(course):
    if request.method == 'POST':
        data = request.json
        subtopic_name = data.get('subtopic')
        course_object = Course.query.filter_by(course_name=course).first()
        if course_object:
            selected_topic = Topic.query.filter_by(course_id=course_object.id, topic_name=data.get('topic')).first()
            if selected_topic:
                subtopic_count = Subtopic.query.filter_by(topic_id=selected_topic.id).count()
                new_subtopic = Subtopic(
                    subtopic_name=subtopic_name,
                    topic_id=selected_topic.id,
                    subtopic_queue=subtopic_count + 1
                )
                db.session.add(new_subtopic)
                db.session.commit()
                return jsonify({'message': 'Successfully added'}), 200
    return jsonify({'error': 'An error occurred while adding the subtopic'}), 500


@app.route('/delete_subtopic/<course>/<topic_id>/<subtopic_id>', methods=['DELETE'])
def delete_subtopic(course, topic_id, subtopic_id):
    if request.method == 'DELETE':
        course_obj = Course.query.filter_by(course_name=course).first()
        topic_obj = Topic.query.filter_by(course_id=course_obj.id, id=topic_id).first()
        subtopic_obj = Subtopic.query.filter_by(topic_id=topic_obj.id, id=subtopic_id).first()

        if subtopic_obj:
            db.session.delete(subtopic_obj)
            db.session.commit()
            return jsonify({'message': 'Subtopic deleted successfully'}), 200
    return jsonify(message='Bad request'), 400


@app.route('/edit_subtopic/<course>/<topic_id>/<subtopic_id>', methods=['PUT'])
def edit_subtopic(course, topic_id, subtopic_id):
    data = request.json
    if request.method == 'PUT':
        course_obj = Course.query.filter_by(course_name=course).first()
        topic_obj = Topic.query.filter_by(course_id=course_obj.id, id=topic_id).first()
        subtopic_obj = Subtopic.query.filter_by(topic_id=topic_obj.id, id=subtopic_id).first()
        subtopic_new_name = data.get('new_name')

        if subtopic_obj:
            subtopic_obj.subtopic_name = subtopic_new_name
            db.session.commit()
            return jsonify({'message': 'Subtopic edited successfully'}), 200
        else:
            return jsonify({'error': 'Subtopic not found'}), 404
    else:
        return jsonify({'error': 'Bad request'}), 400


@app.route('/get_subtopic_by_topic/<topic_name>', methods=['GET'])
def get_subtopic_by_topic(topic_name):
    if request.method == 'GET':
        topic = Topic.query.filter_by(topic_name=topic_name).first()
        if topic:
            subtopics = Subtopic.query.filter_by(topic_id=topic.id).all()
            subtopic_list = []

            for subtopic in subtopics:
                subtopic_data = {
                    "id": subtopic.id,
                    "subtopic": subtopic.subtopic_name,
                    "queue": subtopic.subtopic_queue
                }
                subtopic_list.append(subtopic_data)

            data = {
                "topic": topic_name,
                "subtopics": subtopic_list
            }
            return jsonify(data), 200

        return jsonify({"message": "Topic not found"}), 404

    return jsonify({"message": "Bad request"}), 400


# -----------------------------------------------#
@app.route('/teamlead/dashboard/<username>')
def teamlead_dashboard(username):
    users = User.query.all()  # TODO filter by student
    student_role_id = Role.query.filter_by(role_name='student').first().id
    user_roles = UserRoles.query.filter_by(role_id=student_role_id).all()
    student_user_id_list = [user.user_id for user in user_roles]
    students_list = []
    for user in users:
        if user.id in student_user_id_list:
            usr = User.query.filter_by(username=user.username).first()
            usr_id = usr.id
            fullprg = FullProgress.query.filter_by(id=usr_id).first()
            user.fullprogress = fullprg.progress_value
            students_list.append(user)

    user = User.query.filter_by(username=username).first()
    user_role = UserRoles.query.filter_by(user_id=user.id).first()
    role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
    if role_name == 'teamlead':
        team_id_of_teamlead = TeamLeadOfTeam.query.filter_by(user_id=user.id).first().team_id
        team_of_teamlead = Team.query.filter_by(id=team_id_of_teamlead).first()
        attached_training_course = TrainingCourses.query.filter_by(team_id=team_id_of_teamlead).all()
        attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
                                               attached_training_course]
        available_courses = Course.query.all()
        available_not_attached_courses = set(available_courses).symmetric_difference(
            set(attached_training_course_by_courses))
        return render_template('application/mentor/dashboard/index.html', username=username,
                               users=students_list,
                               attached_training_course_by_courses=attached_training_course_by_courses,
                               available_not_attached_courses=available_not_attached_courses,
                               team_of_teamlead=team_of_teamlead, role_name=role_name)
    elif role_name == 'mentor':
        attached_training_course = MentorOfCourse.query.filter_by(user_id=user.id).all()
        attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
                                               attached_training_course]
        pass


@app.route('/teamlead/course/add', methods=['POST'])
def teamlead_add_course():
    username = current_user.username
    data = request.form
    course_name = data['course']
    teamlead = User.query.filter_by(username=username).first()
    team = TeamLeadOfTeam.query.filter_by(user_id=teamlead.id).first()
    course = Course.query.filter_by(course_name=course_name).first()
    course_queue = data['course_queue']
    if course and team and course_queue:
        attach_course = TrainingCourses(team_id=team.team_id, course_id=course.id, training_queue=course_queue)
        db.session.add(attach_course)
        db.session.commit()
    else:
        flash('name of course is not correct')
    return redirect(url_for('mentor_dashboard', username=username))


@app.route('/teamlead/course/delete-attached-course', methods=['POST'])
def teamlead_delete_course():
    username = current_user.username
    data = request.form
    course_name = data['course']
    if course_name:
        course_id = Course.query.filter_by(course_name=course_name).first().id
        attached_course = TrainingCourses.query.filter_by(course_id=course_id).first()
        db.session.delete(attached_course)
        db.session.commit()
    return redirect(url_for('mentor_dashboard', username=username))


@app.route('/courses/<course_name>')
def courses(course_name):
    username = current_user.username
    course_id = Course.query.filter_by(course_name=course_name).first().id
    course_topics = quick_sort(Topic.query.filter_by(course_id=course_id).all(), attribute='topic_queue')
    course_subtopics = []
    source_by_course_topic = []
    video_source_by_topic = []
    for course_topic in course_topics:
        course_subtopics += Subtopic.query.filter_by(topic_id=course_topic.id).all()
        source_by_course_topic += SourceOfLearningTextContent.query.filter_by(topic_id=course_topic.id).all()
        video_source_by_topic += SourceOfLearningVideoContent.query.filter_by(topic_id=course_topic.id).all()

    source_by_course_subtopics = []
    video_source_by_subtopic = []
    for subtopic in course_subtopics:
        source_by_course_subtopics += SourceOfLearningTextContent.query.filter_by(subtopic_id=subtopic.id).all()
        video_source_by_subtopic += SourceOfLearningVideoContent.query.filter_by(subtopic_id=subtopic.id).all()

    return render_template('application/mentor/coursespage/index.html',
                           username=username,
                           course=course_name,
                           topics=course_topics,
                           subtopics=course_subtopics,
                           source_by_course_topic=source_by_course_topic,
                           source_by_course_subtopics=source_by_course_subtopics,
                           video_source_by_topic=video_source_by_topic,
                           video_source_by_subtopic=video_source_by_subtopic)


@app.route('/courses/<course_name>/add-topic', methods=['POST'])
def courses_add_topic(course_name):
    if request.method == 'POST':
        data = request.form
        if 'topic' in data and 'queue' in data:
            topic_name = data['topic']
            if topic_name:
                queue = data['queue']
                if queue:
                    if queue.isnumeric():
                        course_id = Course.query.filter_by(course_name=course_name).first().id
                        course_topics = Topic.query.filter_by(course_id=course_id).all()
                        topics_id_list = [topic.id for topic in course_topics]
                        if int(queue) not in topics_id_list:
                            topic = Topic(topic_name=topic_name, course_id=course_id, topic_queue=queue)
                            db.session.add(topic)
                            db.session.commit()
                        else:
                            flash('topic queue is available')
                    else:
                        flash('Topic queue can be only numeric')
                else:
                    flash('queue is required')  # TODO
            else:
                flash('topic name is required')
        else:
            flash('topic name and queue is not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/edit-topic', methods=['POST'])
def courses_edit_topic(course_name):
    if request.method == 'POST':
        data = request.form
        if 'topic_id' in data:
            topic_id = int(data['topic_id'])
            if topic_id:
                topic = Topic.query.filter_by(id=topic_id).first()
                if topic:
                    if 'topic_new_queue' in data and 'topic_new_name':
                        topic_new_queue = data['topic_new_queue']
                        topic_new_name = data['topic_new_name']
                        if topic_new_name or topic_new_queue:
                            if topic_new_name:
                                topic.topic_name = topic_new_name
                            if topic_new_queue and topic_new_name.isnumeric():
                                if int(topic_new_queue) != topic.topic_queue:
                                    course_id = Course.query.filter_by(course_name=course_name).first().id
                                    course_topics = Topic.query.filter_by(course_id=course_id).all()
                                    topics_queue_list = [topic.topic_queue for topic in course_topics]
                                    if topic_new_queue in topics_queue_list:
                                        available_topic_with_new_queue = Topic.query.filter_by(course_id=course_id,
                                                                                               topic_queue=topic_new_queue).first()
                                        available_topic_with_new_queue.topic_queue, topic.topic_queue = topic.topic_queue, available_topic_with_new_queue.topic_queue
                                    else:
                                        topic.topic_queue = topic_new_queue
                                else:
                                    topic.topic_queue = topic_new_queue
                            db.session.commit()
                        else:
                            flash('topic new queue or new name is required')
                    else:
                        flash('new queue and new name not in request')
                else:
                    flash('not topic with this id')
            else:
                flash('topic id is required')
        else:
            flash('topic id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/delete-topic', methods=['POST'])
def courses_delete_topic(course_name):
    data = request.form
    if request.method == 'POST':
        if 'topic_id' in data:
            if data['topic_id']:
                topic_id = int(data['topic_id'])
                topic = Topic.query.filter_by(id=topic_id).first()
                db.session.delete(topic)
                db.session.commit()
            else:
                flash('topic id is required')
        else:
            flash('topic id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/add-subtopic', methods=['POST'])
def courses_add_subtopic(course_name):
    if request.method == 'POST':
        data = request.form
        if 'topic_id' in data and 'subtopic' in data and 'queue' in data:
            topic_id = data['topic_id']
            subtopic = data['subtopic']
            subtopic_queue = data['queue']
            if topic_id:
                if subtopic:
                    if subtopic_queue and subtopic_queue.isnumeric():
                        available_queues = [av_subtopic.subtopic_queue for av_subtopic in
                                            Subtopic.query.filter_by(topic_id=int(topic_id)).all()]
                        if int(subtopic_queue) not in available_queues:
                            subtopic = Subtopic(subtopic_name=subtopic, topic_id=topic_id,
                                                subtopic_queue=subtopic_queue)
                            db.session.add(subtopic)
                            db.session.commit()
                        else:
                            flash('queue is available')
                    else:
                        flash('subtopic queue is required and need be a numeric')
                else:
                    flash('subtopic is required')
            else:
                flash('topic id is required')
        else:
            flash('topic id, subtopic name and subtopic queue is not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/edit-subtopic', methods=['POST'])
def courses_edit_subtopic(course_name):
    if request.method == 'POST':
        data = request.form
        if 'subtopic_id' in data:
            if 'new_queue' in data:
                if 'new_subtopic' in data:
                    subtopic_id = data['subtopic_id']
                    new_queue = data['new_queue']
                    new_subtopic = data['new_subtopic']
                    if subtopic_id:
                        if new_queue or new_subtopic:
                            subtopic = Subtopic.query.filter_by(id=subtopic_id).first()
                            if new_subtopic:
                                subtopic.subtopic_name = new_subtopic
                            if new_queue and new_queue.isnumeric():
                                topic_id_of_subtopic = subtopic.topic_id
                                available_subtopic_queue_list = [st.subtopic_queue for st in Subtopic.query.filter_by(
                                    topic_id=topic_id_of_subtopic).all()]
                                if int(new_queue) in available_subtopic_queue_list:
                                    available_subtopic_with_new_queue = Subtopic.query.filter_by(
                                        topic_id=topic_id_of_subtopic, subtopic_queue=new_queue).first()
                                    subtopic.subtopic_queue, available_subtopic_with_new_queue.subtopic_queue = \
                                        available_subtopic_with_new_queue.subtopic_queue, subtopic.subtopic_queue
                                else:
                                    subtopic.subtopic_queue = new_queue
                            db.session.commit()
                        else:
                            flash('new queue or new subtopic name is required')
                    else:
                        flash('subtopic id is required')
                else:
                    flash('new subtopic not in request')
            else:
                flash('new queue not in  request')

        else:
            flash('subtopic id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/delete-subtopic', methods=['POST'])
def courses_delete_subtopic(course_name):
    if request.method == 'POST':
        data = request.form
        if 'subtopic_id' in data:
            subtopic_id = data['subtopic_id']
            if subtopic_id:
                subtopic = Subtopic.query.filter_by(id=subtopic_id).first()
                db.session.delete(subtopic)
                db.session.commit()
            else:
                flash('subtopic id is required')
        else:
            flash('subtopic id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/add-plaintext-content>', methods=['POST'])
def courses_add_plaintext_content(course_name):
    if request.method == 'POST':
        data = request.form
        if 'content_header' in data:
            content_header = data['content_header']
            if 'content_plain_text' in data:
                content_plain_text = data['content_plain_text']
                if content_header:
                    if content_plain_text:
                        if 'topic_id' in data or 'subtopic_id' in data:
                            if 'topic_id' in data:
                                topic_id = data['topic_id']
                                if topic_id:
                                    content = SourceOfLearningTextContent(source_content_header=content_header,
                                                                          source_content_plain_text=content_plain_text,
                                                                          topic_id=topic_id)
                                else:
                                    flash('topic id is required')
                            if 'subtopic_id' in data:
                                subtopic_id = data['subtopic_id']
                                if subtopic_id:
                                    content = SourceOfLearningTextContent(source_content_header=content_header,
                                                                          source_content_plain_text=content_plain_text,
                                                                          subtopic_id=subtopic_id)
                                else:
                                    flash('subtopic id is required')
                            db.session.add(content)
                            db.session.commit()
                        else:
                            flash('topic id and subtopic id not in request')
                    else:
                        flash('Content is required')
                else:
                    flash('content header is required')
            else:
                flash('content plain text not in request')
        else:
            flash('content header not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/edit-plaintext-content>', methods=['POST'])
def courses_edit_plaintext_content(course_name):
    if request.method == 'POST':
        data = request.form
        if 'content_id' in data:
            if 'new_header' in data:
                if 'new_content_plain_text' in data:
                    content_id = data['content_id']
                    new_header = data['new_header']
                    new_content_plain_text = data['new_content_plain_text']
                    if content_id:
                        content = SourceOfLearningTextContent.query.filter_by(id=content_id).first()
                        if new_header or new_content_plain_text:
                            if new_header:
                                content.source_content_header = new_header
                            if new_content_plain_text:
                                content.source_content_plain_text = new_content_plain_text
                            db.session.commit()
                        else:
                            flash('content header or content plain text is required')

                    else:
                        flash('content id is required')
                else:
                    flash('content plain text not in request')
            else:
                flash('content header not in request')
        else:
            flash('content id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/delete-plaintext-content>', methods=['POST'])
def courses_delete_plaintext_content(course_name):
    if request.method == 'POST':
        data = request.form
        if 'content_id' in data:
            content_id = data['content_id']
            if content_id:
                content = SourceOfLearningTextContent.query.filter_by(id=content_id).first()
                db.session.delete(content)
                db.session.commit()
            else:
                flash('content id is required')
        else:
            flash('content id not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/upload-video-content>', methods=['POST'])
def courses_upload_video_content(course_name):
    if request.method == 'POST':
        data = request.form
        if 'video_name' in data:
            if 'queue' in data:
                if 'subtopic_id' in data or 'topic_id' in data:
                    subtopic_id = data.get('subtopic_id')
                    topic_id = data.get('topic_id')
                    video_name = data['video_name']
                    queue = data['queue']
                    if subtopic_id:
                        subtopic_name_or_topic_name = Subtopic.query.filter_by(id=subtopic_id).first().subtopic_name
                    else:
                        subtopic_name_or_topic_name = Topic.query.filter_by(id=topic_id).first().topic_name
                    if video_name and queue:
                        if 'file' in request.files:
                            file = request.files['file']
                            if file.filename:
                                upload_root_path = os.path.join(app.config["UPLOAD_FOLDER"])
                                sec_filename = secure_filename(file.filename)
                                file_path = save_file(file=file,
                                                      course_name=course_name,
                                                      topic_subtopic=subtopic_name_or_topic_name,
                                                      sec_filename=sec_filename,
                                                      root_path=upload_root_path)
                                if file_path:
                                    video_content = SourceOfLearningVideoContent(video_name=video_name,
                                                                                 video_path=file_path,
                                                                                 topic_id=topic_id,
                                                                                 subtopic_id=subtopic_id,
                                                                                 video_queue=queue)
                                    db.session.add(video_content)
                                    db.session.commit()
                            else:
                                flash('File not selected')
                        else:
                            flash('file not in request')
                    else:
                        flash('video name and video queue is required')
                else:
                    flash('topic id and subtopic id not in request')
            else:
                flash('queue not in request')
        else:
            flash('video name not in request')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/edit-video-content>', methods=['POST'])
def courses_edit_video_content(course_name):
    if request.method == "POST":
        data = request.form
        if 'id' in data:
            source_video_id = data['id']
            source_video = SourceOfLearningVideoContent.query.filter_by(id=source_video_id).first()
            if 'video_queue' or 'video_name' or 'video_content' in data:
                video_queue = data['video_queue']
                video_name = data['video_name']
                video_path = data['video_path']
                if video_queue:
                    source_video.video_queue = video_queue
                if video_name:
                    source_video.video_name = video_name
                if video_path:
                    if 'file' in request.files:
                        file = request.files['file']
                        if file.filename:
                            upload_root_path = os.path.join(app.config["UPLOAD_FOLDER"])
                            sec_filename = secure_filename(file.filename)
                            file_path = save_file(file=file,
                                                  course_name=course_name,
                                                  topic_subtopic=subtopic_name_or_topic_name,
                                                  sec_filename=sec_filename,
                                                  root_path=upload_root_path)
                            if file_path:
                                video_content = SourceOfLearningVideoContent(video_name=video_name,
                                                                             video_path=file_path,
                                                                             topic_id=topic_id,
                                                                             subtopic_id=subtopic_id,
                                                                             video_queue=queue)
                                db.session.add(video_content)
                                db.session.commit()
                    source_video.video_path = video_path
            else:
                flash('wideo queue or video name or video content required')
        else:
            flash('id is required')


@app.route('/courses/<course_name>/delete-video-content>', methods=['POST'])
def courses_delete_video_content(course_name):
    if request.method == 'POST':
        data = request.form
        if 'id' in data:
            source_video_id = data['id']
            source_video = SourceOfLearningVideoContent.query.filter_by(id=source_video_id).first()
            path_of_video = source_video.video_path
            db.session.delete(source_video)
            db.session.commit()
            os.remove(path_of_video)
        else:
            flash('id for video required')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    return render_template('pagenotfound/index.html')


@app.route('/test/<name>/<age>')
def test(name, age):
    return f'<h1>{name}-{age}</h1>'
