# from flask_security import roles_required
from datetime import datetime

from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required

from app import app, db, login_manager
from helpers import generate_hash
from models import User, Course, Team, Role, UserRoles, MentorOfCourse, TeamLeadOfTeam


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/admin/login', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def login_admin():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username, password=generate_hash(password)).first()
        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify(message='Invalid username or password'), 401
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/get_<userrole>s')
@jwt_required()
def get_users(userrole):
    if request.method == 'GET':
        role_id = Role.query.filter_by(role_name=userrole).first()
        if role_id:
            admin_list_by_id = UserRoles.query.filter_by(role_id=role_id.id).all()
            admin_list = [User.query.filter_by(id=user.id).first() for user in admin_list_by_id]
            return jsonify({f'{userrole}s': [user.user_to_dict() for user in admin_list]}), 200
        else:
            return jsonify(message='bad request'), 400
    else:
        return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/get_teams')
@jwt_required()
def get_teams():
    if request.method == 'GET':
        teams = Team.query.all()
        teams_list = [team.team_to_dict() for team in teams]
        return jsonify(teams=teams_list), 200
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/get_courses')
@jwt_required()
def get_courses():
    if request.method == 'GET':
        courses = Course.query.all()
        course_list = [course.course_to_dict() for course in courses]
        return jsonify(courses=course_list), 200
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/register_user', methods=['POST'])
@jwt_required()
def register_user():
    if request.method == 'POST':
        data = request.json
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        birthday = data.get('birthday')
        role = data.get('role')
        if firstname and lastname and username and email and phone and password and birthday and role:
            if not User.query.filter_by(username=username).first():
                user = User(firstname=firstname,
                            lastname=lastname,
                            username=username,
                            email=email,
                            phone=phone,
                            password=generate_hash(password),
                            birthday=datetime.strptime(birthday, "%Y-%m-%d").date())
                db.session.add(user)
                db.session.commit()
                role = Role.query.filter_by(role_name=role).first()
                user_id = User.query.filter_by(username=username).first().id
                role_id = role.id
                user_role = UserRoles(user_id=user_id, role_id=role_id)
                db.session.add(user_role)
                db.session.commit()
                return jsonify(message='Successfully registered'), 200
        return jsonify(message='bad request'), 400
    return jsonify(message='Method Not Allowed'), 405


# ---Samo---#
@app.route('/admin/edit_user/<id>', methods=['PUT'])
@jwt_required()
def edit_user(id):
    if request.method == "PUT":
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.json
            new_firstname = data.get('firstname')
            new_lastname = data.get('lastname')
            new_username = data.get('username')
            new_email = data.get('email')
            new_phone = data.get('phone')
            new_password = data.get('password')
            new_birthday = data.get('birthday')
            new_role = data.get('role')

            user.firstname = new_firstname
            user.lastname = new_lastname
            user.username = new_username
            user.email = new_email
            user.phone = new_phone
            user.password = generate_hash(new_password)
            user.birthday = datetime.strptime(new_birthday, "%Y-%m-%d").date()

            role = Role.query.filter_by(role_name=new_role).first()
            if role:
                user.roles = [role]

            db.session.commit()
            return jsonify(message='Successfully edited'), 200
        return jsonify(message='User not found'), 404
    return jsonify(message='Method Not Allowed'), 405


# ---Samo---#


@app.route('/admin/delete_user/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    if request.method == 'DELETE':
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            return jsonify(message='bad request'), 400
    return jsonify({'message': 'User deleted successfully'}), 200


@app.route('/admin/attache_mentor_course', methods=['POST'])
@jwt_required()
def attache_mentor_course():
    data = request.json
    if request.method == 'POST':
        course_id = data.get('course_id')
        mentor_id = data.get('mentor_id')
        if mentor_id and course_id:
            attach_mentor = MentorOfCourse(user_id=mentor_id, course_id=course_id)
            db.session.add(attach_mentor)
            db.session.commit()
            return jsonify({'message': 'Mentor attached successfully'}), 200
        else:
            return jsonify(message='bad request'), 400


@app.route('/admin/add_course', methods=['POST'])
@jwt_required()
def admin_add_course():
    data = request.json
    if request.method == 'POST':
        course_name = data.get('course_name')
        if course_name:
            course = Course(course_name=course_name)
            db.session.add(course)
            db.session.commit()
            return jsonify({'message': 'Course add successfully'}), 200
        else:
            return jsonify(message='bad request'), 400
    else:
        return jsonify(message='bad request'), 400


@app.route('/admin/edit_course', methods=['PUT'])
@jwt_required()
def admin_edit_course():
    data = request.json
    if request.method == 'PUT':
        course_id = data.get('id')
        course_new_name = data.get('course_new_name')
        course = Course.query.filter_by(id=course_id).first()
        if course:
            course.course_name = course_new_name
            db.session.commit()
            return jsonify({'message': 'Course edited successfully'}), 200
        else:
            jsonify(message='bad request'), 400
    return jsonify(message='bad request'), 400


@app.route('/admin/delete_course/<id>', methods=['DELETE'])
@jwt_required()
def admin_delete_course(id):
    if request.method == 'DELETE':
        course = Course.query.filter_by(id=id).first()
        if course:
            db.session.delete(course)
            db.session.commit()
        else:
            return jsonify(message='bad request'), 400
    return jsonify({'message': 'Course deleted successfully'}), 200

#---Samo---#
@app.route('/admin/add_team', methods=['POST'])
@jwt_required()
def admin_add_team():
    date = request.json
    if request.method == 'POST':
        team_name = date.get('team_name')
        if team_name:
            team = Team(team_name=team_name)
            db.session.add(team)
            db.session.commit()
            return jsonify({'message': 'Team added successfully'}), 200
        else:
            return jsonify(message='bad request'), 400
    else:
        return jsonify(message='bad request'), 400
#---Samo---#

#---Samo---#
@app.route('/admin/edit_team', methods=['PUT'])
@jwt_required()
def admin_edite_team():
    data = request.json
    if request.method == 'PUT':
        team_id = data.get('id')
        team_new_name = data.get('team_new_name')
        team = Team.query.filter_by(id=team_id).first()
        if team:
            team.team_name = team_new_name
            db.session.commit()
            return jsonify({'message': 'Team edited successfully'}), 200
        else:
            return jsonify(message='bad request'), 400
    else:
        return jsonify(message='bad request'), 400
#---Samo---#


#---Samo---#
@app.route('/admin/delete_team/<id>', methods=['DELETE'])
@jwt_required()
def admin_delete_team(id):
    if request.method == 'DELETE':
        team = Team.query.filter_by(id=id).first()
        if team:
            db.session.delete(team)
            db.session.commit()
        else:
            return jsonify(message='bad request'), 400
    return jsonify({'message': 'Team deleted successfully'}), 200
#---Samo---#



@app.route('/admin/attach_user_to_team', methods=['POST'])
@jwt_required()
def attache_teamlead_course():
    data = request.json
    if request.method == 'POST':
        team_id = data.get('team_id')
        user_id = data.get('user_id')
        if user_id and team_id:
            attach_user = TeamLeadOfTeam(user_id=user_id, team_id=team_id)
            db.session.add(attach_user)
            db.session.commit()
            return jsonify({'message': 'User attached successfully'}), 200
        else:
            return jsonify({'message': 'user or Team does not exist'}), 405
    return jsonify(message='bad request'), 400












# @app.route('/admin', methods=['GET', 'POST'])
# @app.route('/admin/', methods=['GET', 'POST'])
# # @roles_required('admin')
# def admin():
#     form = LoginForm()
#     if request.method == 'POST':
#         data = request.form
#         username = data['username']
#         user = User.query.filter_by(username=username).first()
#
#         if user:
#             if data['username'] == user.username and generate_hash(data['password']) == user.password:
#                 login_user(user)
#                 return redirect(url_for('admin_dashboard', username=user.username))
#             else:
#                 error_message = 'Wrong password'
#                 return render_template('admin/loginform/index.html', form=form, error=error_message)
#         else:
#             error_message = 'Wrong username'
#             return render_template('admin/loginform/index.html', form=form, error=error_message)
#     return render_template('admin/loginform/index.html', form=form)
#
#
# @app.route('/admin/logout')
# def admin_logout():
#     logout_user()
#     return redirect(url_for('admin'))
#
#
# @app.route('/admin/dashboard')
# @app.route('/admin/dashboard/<username>')
# # @login_required
# def admin_dashboard(username):
#     users = User.query.all()
#     teams = Team.query.all()
#     teamlead_role = Role.query.filter_by(role_name='teamlead').first()
#     all_teamleads_in_user_role = UserRoles.query.filter_by(role_id=teamlead_role.id)
#     attached_teamleads_id_list = [user.user_id for user in TeamLeadOfTeam.query.all()]
#     team_leads_wthout_team = []
#     for lead in all_teamleads_in_user_role:
#         if lead.user_id not in attached_teamleads_id_list:
#             team_leads_wthout_team.append(User.query.filter_by(id=lead.user_id).first())
#     attached_teams_id_list = [team.team_id for team in TeamLeadOfTeam.query.all()]
#     teams_without_lead = []
#     for team in teams:
#         if team.id not in attached_teams_id_list:
#             teams_without_lead.append(team)
#     team_attached_to_team_lead = TeamLeadOfTeam.query.all()
#     team_and_teamlead = [(Team.query.filter_by(id=attached_team_andteamlead.team_id).first(),
#                           User.query.filter_by(id=attached_team_andteamlead.user_id).first()) for
#                          attached_team_andteamlead in
#                          team_attached_to_team_lead]
#     for user in users:
#         role_id = UserRoles.query.filter_by(user_id=user.id).first().role_id
#         role = Role.query.filter_by(id=role_id).first().role_name
#         user.role = role
#     roles = Role.query.all()
#     avalaible_courses = Course.query.all()
#     attached_mentor_id_set = set([mentor.user_id for mentor in MentorOfCourse.query.all()])
#     attached_mentor_to_course = []
#     for mentor_id in attached_mentor_id_set:
#         one_mentor_attached_courses = MentorOfCourse.query.filter_by(user_id=mentor_id).all()
#         one_mentor_attached_courses_names = [Course.query.filter_by(id=attached_course.course_id).first().course_name
#                                              for
#                                              attached_course in one_mentor_attached_courses]
#         mentor_and_courses = (User.query.filter_by(id=mentor_id).first().username, one_mentor_attached_courses_names)
#         attached_mentor_to_course.append(mentor_and_courses)
#
#     form = RegisterForm()
#     return render_template('admin/dashboard/index.html',
#                            username=username,
#                            users=users,
#                            form=form,
#                            roles=roles,
#                            teams=teams,
#                            team_leads_wthout_team=team_leads_wthout_team,
#                            teams_without_lead=teams_without_lead,
#                            team_and_teamlead=team_and_teamlead,
#                            avalaible_courses=avalaible_courses,
#                            attached_mentor_to_course=attached_mentor_to_course, now_date=date.today())
#
#
# @app.route('/admin/dashboard_css/delete/<user_id>')
# # @login_required
# def admin_delete_user(user_id):
#     user = User.query.filter_by(id=user_id)
#     db.session.delete(user)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))
#
#
# @app.route('/admin/daashboard/edit/<user_id>')
# # @login_required
# def admin_edit_user(user_id):
#     user = User.query.filter_by(id=user_id)
#     data = request.form  # TODO chack from form data can not be empty
#     user.firstname = data['firstname']
#     user.lastname = data['lastname']
#     user.username = data['lastname']
#     user.email = data['email']
#     user.phone = data['phone']
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))
#
#
# @app.route('/admin/register', methods=['POST'])
# # @login_required
# def admin_register():
#     # form = RegisterForm()
#     if request.method == 'POST':
#         data = request.form
#         # if form.validate_on_submit():
#         birthday = datetime.strptime(data['birthday'], "%Y-%m-%d").date()
#         user = User(firstname=data['firstname'],
#                     lastname=data['lastname'],
#                     username=data['username'],
#                     password=generate_hash(data['password']),
#                     birthday=birthday,
#                     email=data['email'],
#                     phone=data['phone'])
#         db.session.add(user)
#         db.session.commit()
#         added_user = User.query.filter_by(username=user.username).first()
#         added_user_id = added_user.id
#         fullprogress = FullProgress(progress_value=0, user_id=added_user_id)
#         db.session.add(fullprogress)
#         db.session.commit()
#         role = Role.query.filter_by(role_name=data['role']).first()
#         role_id = role.id
#         user_role = UserRoles(user_id=added_user_id, role_id=role_id)
#         db.session.add(user_role)
#         db.session.commit()
#     username = current_user.username
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/team/add', methods=['POST'])
# # @login_required
# def admin_add_team():
#     username = current_user.username
#     data = request.form
#     team_name = data['team']
#     check_team_avalblity = Team.query.filter_by(team_name=team_name).first()
#     if not check_team_avalblity and team_name:
#         team = Team(team_name=team_name)
#         db.session.add(team)
#         db.session.commit()
#         return redirect(url_for('admin_dashboard', username=username))
#     else:
#         flash('Team exists')
#         return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/team/delete', methods=['POST'])
# def admin_team_delete():
#     username = current_user.username
#     data = request.form
#     team = Team.query.filter_by(team_name=data['teamname']).first()
#     db.session.delete(team)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/course/add', methods=['POST'])
# def admin_add_course():
#     username = current_user.username
#     data = request.form
#     course_name = data['course']
#     check_course_avalability = Course.query.filter_by(course_name=course_name).first()
#     if not check_course_avalability and course_name:
#         course = Course(course_name=course_name)
#         db.session.add(course)
#         db.session.commit()
#     else:
#         flash('course already exists')
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/course/delete', methods=['POST'])
# def admin_delete_course():
#     username = current_user.username
#     data = request.form
#     course_name = data['coursename']
#     course = Course.query.filter_by(course_name=course_name).first()
#     db.session.delete(course)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/attach_teamlead', methods=['POST'])
# def admin_attach_teamlead():
#     username = current_user.username
#     data = request.form
#     team_name = data['team']
#     lead_name = data['lead']
#     lead_id = User.query.filter_by(username=lead_name).first().id
#     team_id = Team.query.filter_by(team_name=team_name).first().id
#     team_lead_of_team_by_team = TeamLeadOfTeam.query.filter_by(team_id=team_id).first()
#     team_lead_of_team_by_lead = TeamLeadOfTeam.query.filter_by(user_id=lead_id).first()
#     if not team_lead_of_team_by_team:
#         if not team_lead_of_team_by_lead:
#             team_lead_of_team = TeamLeadOfTeam(team_id=team_id, user_id=lead_id)
#             db.session.add(team_lead_of_team)
#             db.session.commit()
#         else:
#             flash(f'{lead_name} attached on another team')
#     else:
#         flash(f'{team_name} already have teamlead')
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/delete-attached-teamlead', methods=['POST'])
# def admin_delete_attached_teamlead():
#     username = current_user.username
#     data = request.form
#     user_id = User.query.filter_by(username=data['username']).first().id
#     team_id = Team.query.filter_by(team_name=data['teamname']).first().id
#     team_lead_of_team = TeamLeadOfTeam.query.filter_by(user_id=user_id, team_id=team_id).first()
#     db.session.delete(team_lead_of_team)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/attach-mentor-course', methods=['POST'])
# def admin_attach_course_mentor():
#     username = current_user.username
#     data = request.form
#     mentor = User.query.filter_by(username=data['mentor']).first()
#     course = Course.query.filter_by(course_name=data['course']).first()
#     if mentor and course:
#         check_mentor_avalability = MentorOfCourse.query.filter_by(user_id=mentor.id, course_id=course.id).first()
#         if not check_mentor_avalability:
#             attach_mentor = MentorOfCourse(user_id=mentor.id, course_id=course.id)
#             db.session.add(attach_mentor)
#             db.session.commit()
#         else:
#             flash('mentor already attached to course')
#     else:
#         flash('')  # TODO
#     return redirect(url_for('admin_dashboard', username=username))
#
#
# @app.route('/admin/delete-mentor-from-course')
# def admin_delete_mentor_from_course():
#     data = request.data
#
#     pass
