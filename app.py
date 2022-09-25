from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.hbsrzff.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta_plus_week4


@app.route('/')
def home():
    schedule_list = list(db.schedule.find({}, {'_id': False}))
    schedule_list = (sorted(schedule_list, key=lambda x: x['date']))
    return render_template('index.html', schedules=schedule_list)


@app.route("/schedule", methods=["POST"])
def schedule_post():
    schedule_receive = request.form['schedule_give']
    date_receive = request.form['date_give']

    schedule_list = list(db.schedule.find({}, {'_id': False}))
    count = len(schedule_list) + 1
    doc = {
        'num': count,
        'schedule': schedule_receive,
        'done': 0,
        'date': date_receive,

    }
    db.schedule.insert_one(doc)

    return jsonify({'msg': '등록완료!'})


@app.route("/schedule/done", methods=["POST"])
def schedule_done():
    num_receive = request.form['num_give']

    db.schedule.update_one({'num': int(num_receive)}, {'$set': {'done': 1}})
    return jsonify({'msg': '완료'})


@app.route("/schedule/undo", methods=["POST"])
def schedule_undo():
    num_receive = request.form['num_give']

    db.schedule.update_one({'num': int(num_receive)}, {'$set': {'done': 0}})
    return jsonify({'msg': '취소 완료'})


@app.route("/schedule", methods=["GET"])
def schedule_get():
    schedule_list = list(db.schedule.find({}, {'_id': False}))

    schedule_list = (sorted(schedule_list, key=lambda x: x['date']))

    return jsonify({'schedules': schedule_list})


@app.route('/login')
def login():
    msg = request.args.get("msg")

    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 사용한다-----------
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']


    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
    "username": username_receive,  # 아이디
    "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 사용한다-------------
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']

    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
