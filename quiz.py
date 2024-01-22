import difflib
import random
from flask import Flask, render_template, session, request, redirect
import json
import datetime
import uuid
from logic import send_email_message, get_user_info, check_level

app = Flask(__name__)
app.secret_key = "key"

users = []
quiz = []

try:
    with open('json/users.json', 'r') as file:
        users = json.loads(file.read())
    with open('json/quiz.json', 'r') as file:
        quiz = json.loads(file.read())
except Exception as e:
    print(e)


def save_users():
    with open('json/users.json', 'w') as file:
        file.write(json.dumps(users, ensure_ascii=False))
    with open('json/quiz.json', 'w') as file:
        file.write(json.dumps(quiz, ensure_ascii=False))

@app.route('/')
def hello_world():
    if session.get('auth', False) == False:
        return render_template('main.html', auth=0)
    else:
        return render_template('main.html',
                               auth=1,
                               quizes=quiz,
                               user=session['auth'],
                               user_info=get_user_info(session['auth'], quiz)
                               )


@app.route("/register", methods=['POST'])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    users.append({
        "name": name,
        "email": email,
        "password": password,
        "solved": 0,
        "level": "Рекрут",
        "ranked": "Дерево",
        "image": "https://avatars.dzeninfra.ru/get-zen_doc/1877575/pub_5fa4f42e3a59d851051d79cf_5fa4f4cc3a59d851051e6147/scale_1200",
        "points": 0,
        "rewards": []
    })
    save_users()
    session["auth"] = email
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    email = request.form.get("email")
    for element in users:
        if element['email'] == email and password == element['password']:
            session['auth'] = email
            return redirect("/")
    return render_template("main.html", alert="Неверный логин или пароль", auth=0)


@app.route("/logout")
def logout():
    del session['auth']
    return redirect("/")


@app.route("/create", methods=['POST'])
def create():
    pages = int(request.form.get("number"))
    name = request.form.get("name")
    return render_template("create.html", pages=pages, name=name)


@app.route("/create/<int:pages>/<name>", methods=['POST'])
def create_pages_name(pages, name):
    if pages < 1:
        return render_template("main.html",
                               user_info=get_user_info(session['auth'], quiz),
                               quizes=quiz,
                               user=session['auth'],
                               alert="Количество вопросов не может быть меньше одного",
                               auth=1
                               )
    quiz_list = []
    for i in range(int(pages)):
        if request.form.get(f"reg{i + 1}") == None:
            ignoreReg = False
        else:
            ignoreReg = True
        quiz_list.append({
            "title": request.form.get(f"title{i + 1}"),
            "text": request.form.get(f"text{i + 1}"),
            "answer": request.form.get(f"answer{i + 1}"),
            "color": request.form.get(f"color{i + 1}"),
            "alter": request.form.get(f"alter{i + 1}"),
            "point": request.form.get(f"point{i + 1}"),
            "image": request.form.get(f"image{i + 1}"),
            "hint": request.form.get(f"hint{i + 1}"),
            "proc": request.form.get(f"proc{i + 1}"),
            "ignoreReg": ignoreReg,
        })
    print(quiz_list)

    if request.form.get("hidden") == None:
        hidden = False
    else:
        hidden = True
    if request.form.get("once") == None:
        once = False
    else:
        once = True
    if request.form.get("noti") == None:
        noti = False
    else:
        noti = True
    if request.form.get("anonim") == None:
        anonim = False
    else:
        anonim = True

    time = request.form.get("time")
    if time.isnumeric():
        time = int(time) * 1000
    else:
        time = 0

    quiz.append({
        "author": session['auth'],
        "value": 0.0,
        "solved": 0,
        "name": name,
        "number": str(random.randint(100000, 999999)),
        "quizes": quiz_list,
        "results": [],
        "review": [],
        "once": once,
        "hidden": hidden,
        "noti": noti,
        "learn": request.form.get("learn"),
        "anonim": anonim,
        "time": time,
        "open": True
    })
    save_users()
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Квиз был успешно создан, теперь он доступен всем пользователям",
                           auth=1
                           )


@app.route("/edit/<id>", methods=['GET'])
def edit(id):
    for q in quiz:
        if q['number'] == id:
            return render_template("edit.html", quiz=q)
    return redirect("/")


@app.route("/edit/<id>", methods=['POST'])
def edit_post(id):
    for q in quiz:
        if q['number'] == id:
            quiz_list = []
            for i in range(len(q['quizes'])):
                if request.form.get(f"reg{i + 1}") == None:
                    ignoreReg = False
                else:
                    ignoreReg = True
                quiz_list.append({
                    "title": request.form.get(f"title{i + 1}"),
                    "text": request.form.get(f"text{i + 1}"),
                    "answer": request.form.get(f"answer{i + 1}"),
                    "color": request.form.get(f"color{i + 1}"),
                    "alter": request.form.get(f"alter{i + 1}"),
                    "point": request.form.get(f"point{i + 1}"),
                    "image": request.form.get(f"image{i + 1}"),
                    "hint": request.form.get(f"hint{i + 1}"),
                    "proc": request.form.get(f"proc{i + 1}"),
                    "ignoreReg": ignoreReg,
                })
            if request.form.get("hidden") == None:
                hidden = False
            else:
                hidden = True
            if request.form.get("once") == None:
                once = False
            else:
                once = True
            if request.form.get("noti") == None:
                noti = False
            else:
                noti = True
            if request.form.get("anonim") == None:
                anonim = False
            else:
                anonim = True

            time = request.form.get("time")
            if type(time) == int:
                time = time * 100000
            else:
                time = None

            q['quizes'] = []
            q['quizes'] = quiz_list
            q['noti'] = noti
            q['once'] = once
            q['anonim'] = anonim
            q['hidden'] = hidden
            q['learn'] = request.form.get("learn")
            q['time'] = time
            save_users()

    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Квиз был успешно изменен",
                           auth=1
                           )


@app.route("/find", methods=['POST'])
def find():
    id = request.form.get("number")
    return redirect(f"/open/{id}")


@app.route("/open/<id>")
def open_id(id):
    for q in quiz:
        if q['number'] == id:
            if q['open'] == False:
                return render_template("main.html",
                                       user_info=get_user_info(session['auth'], quiz),
                                       quizes=quiz,
                                       user=session['auth'],
                                       alert=f"Данный квиз закрыт. За подробностями обратитесь к создателю квиза - {q['author']}",
                                       auth=1
                                       )

            if q['once'] == True:
                for a in q['results']:
                    if a['user'] == session['auth']:
                        return render_template("main.html",
                                               user_info=get_user_info(session['auth'], quiz),
                                               quizes=quiz,
                                               user=session['auth'],
                                               alert="Вы уже проходили данный квиз. Он был доступен для прохождения только один раз!",
                                               auth=1
                                               )
                return render_template("show.html", quiz=q, alert="Учтите, что вы сможете пройти квиз только один раз!")
            else:
                return render_template("show.html", quiz=q)
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           alert=f"Квиз с таким номером найден не был",
                           auth=1
                           )


@app.route("/result/<id>")
def result_id(id):
    for q in quiz:
        if q['number'] == id:
            return render_template("answers.html", results=q['results'])
    return redirect("/")


@app.route("/del/<id>")
def del_id(id):
    for q in range(len(quiz) + 1):
        if quiz[q]['number'] == id and session['auth'] == quiz[q]['author']:
            del quiz[q]
            save_users()
            break
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Квиз успешно удален",
                           auth=1
                           )


@app.route("/status/<id>")
def status(id):
    st = True
    for q in range(len(quiz) + 1):
        if quiz[q]['number'] == id and session['auth'] == quiz[q]['author']:
            if quiz[q]['open'] == True:
                quiz[q]['open'] = False
            else:
                quiz[q]['open'] = True
            st = quiz[q]['open']
            save_users()
            break
    if st == True:
        st = "открыт"
    else:
        st = "закрыт"
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Статус успешно изменен, теперь квиз {st}",
                           auth=1
                           )


@app.route("/solve/<number>", methods=['POST'])
def solve_number(number):
    answers = []
    points = 0
    for q in quiz:
        if q['number'] == number:
            for i in range(len(q['quizes'])):
                if q['quizes'][i]["ignoreReg"] == True:
                    now_ans = request.form.get(f"answer{i + 1}").lower()
                    real_ans = q['quizes'][i]['answer'].lower()
                    alter_ans = q['quizes'][i]['alter'].lower()
                else:
                    now_ans = request.form.get(f"answer{i + 1}")
                    real_ans = q['quizes'][i]['answer']
                    alter_ans = q['quizes'][i]['alter']

                # if q['quizes'][i]['proc']:
                #     match = difflib.SequenceMatcher(None, real_ans, alter_ans)
                #     value = match.ratio()
                #     value = float(value)
                #     value = round(value, 2)
                #     if value >= int(q['quizes'][i]['proc']) / 100:
                #         answers.append({
                #             "result": True,
                #             "answer": request.form.get(f"answer{i + 1}"),
                #         })
                #         point = int(request.form.get(f"point{i + 1}"))
                #         points += point
                #     else:
                #         answers.append({
                #             "result": False,
                #             "answer": request.form.get(f"answer{i + 1}"),
                #             "true": q['quizes'][i]['answer']
                #         })
                # else:
                if now_ans == real_ans or now_ans == alter_ans:
                    answers.append({
                        "result": True,
                        "answer": request.form.get(f"answer{i + 1}"),
                    })
                    point = int(request.form.get(f"point{i + 1}"))
                    points += point
                else:
                    answers.append({
                        "result": False,
                        "answer": request.form.get(f"answer{i + 1}"),
                        "true": q['quizes'][i]['answer']
                    })
            print(answers)
            true = 0
            false = 0
            count = 0
            for j in answers:
                if j['result'] == True:
                    true += 1
                    count += 1
                else:
                    false += 1
                    count += 1
            percent = round((true / count) * 100)
            name = ""
            for user in users:
                if user['email'] == session['auth']:
                    name = user['name']
            if q['anonim'] == True:
                name = "Аноним"
            q['results'].append({
                "user": session['auth'],
                "rating": percent,
                "data": datetime.datetime.now().strftime("%m-%d %H:%M"),
                "name": name,
                "result": answers,
                "points": points
            })
            save_users()

            if q['noti'] == True:
                send_email_message(q['author'],
                                   f"<h3>Ответ на квиз</h3><p>Пользователь {session['auth']} прошел квиз {q['name']} на {percent}%</p>",
                                   "Ответ на квиз")
            if q['hidden'] == True:
                percent = None
                answers = None

            for u in range(len(users)):
                if session['auth'] == users[u]['email']:
                    users[u]['points'] += points
                    users[u]['solved'] += 1
                    users[u]['level'] = check_level(users[u]['points'])

                    break
            save_users()

            return render_template("result.html", percent=percent, answers=answers, author=q['author'], points=points, id=number)
    return redirect("/")

@app.route("/help", methods=['POST'])
def help():
    text = request.form.get("ask")
    send_email_message(
        "admin@banjosurf.ru",
        f"Пользователь {session['auth']} задал вопрос: <i>'{text}'</i>",
        "Вопрос от пользователя"
    )
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Спасибо за вопрос! Администратор все проверит и ответит вам в течении дня нескольких часов",
                           auth=1
                           )

@app.route("/review/<id>", methods=['POST'])
def review(id):
    value = request.form.get("value")
    text = request.form.get("text")
    for q in range(len(quiz) + 1):
        if quiz[q]['number'] == id:
            quiz[q]['review'].append({
                "user": session['auth'],
                "value": value,
                "text": text
            })
            quiz[q]['solved'] = quiz[q]['solved'] + 1
            quiz[q]['value'] = (quiz[q]['value'] + int(value)) / quiz[q]['solved']
            save_users()
            return render_template("main.html",
                                   user_info=get_user_info(session['auth'], quiz),
                                   quizes=quiz,
                                   user=session['auth'],
                                   good=f"Спасибо за отзыв!",
                                   auth=1
                                   )
            break
    return redirect('/')

@app.route("/report/<id>")
def report(id):
    send_email_message(
        "admin@banjosurf.ru",
        f"Пользователь {session['auth']} пожаловался на квиз №{id}, примите необходимые меры",
        "Уведомление от пользователя"
    )
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           good=f"Спасибо за жалобу! Администратор все проверит и примет необходимые меры",
                           auth=1
                           )

@app.route("/timer")
def timer():
    return render_template("main.html",
                           user_info=get_user_info(session['auth'], quiz),
                           quizes=quiz,
                           user=session['auth'],
                           alert=f"К сожалению, вы не успели пройти квиз",
                           auth=1
                           )

@app.route('/new')
def new_quiz():
    return render_template('new/new.html')

app.run(port=5001)
