# bin/bash
#python -m venv classroom_env
#source classroom_env/bin/activate
#pip install -r requirements.txt

python -c "from app import create_db; create_db()"
sqlite3 classroom.db "insert into user(firstname, lastname, username, password, email, phone, birthday, create_date) values('admin', 'admin', 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@admin.am', '123456', '21-07-1985', '2023-02-01');"
sqlite3 classroom.db "insert into role(role_name) values('superuser');"
sqlite3 classroom.db "insert into role(role_name) values('admin');"
sqlite3 classroom.db "insert into role(role_name) values('teamlead');"
sqlite3 classroom.db "insert into role(role_name) values('mentor');"
sqlite3 classroom.db "insert into role(role_name) values('student');"
sqlite3 classroom.db "insert into full_progress(progress_value, user_id) values(0,1);"
sqlite3 classroom.db "insert into roles_users(user_id, role_id) values(1, 2);"
python app.py
