# python app.py
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from models import db, User, Game, Rating, Feedback


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'nik111nik'
db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/photo/<path:filename>')
def serve_photo(filename):
    return send_from_directory('photo', filename)

@app.route('/')
def welcome():
    '''
    Функция переводит пользователя на главный экран приложения.
    '''
    return render_template('welcome.html')

@app.route('/regist_user/', methods=['GET', 'POST'])
def regist_user():
    '''
    Функция возвращает форму для регистрации пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при регистрации пользователя,
    и добавляет её в базу данных.
    Если логин уже есть в базе данных, то выводится сообщение "Логин уже занят((( Попробуйте другой"
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first() is None:
            user = User(username=username, firstname=firstname, lastname=lastname, password=password)
            db.session.add(user)
            db.session.commit()
            return render_template('welcome_user.html', username=username, user_id=user.id)
        else:
            return "Логин уже занят((( Попробуйте другой"

    return render_template('regist_user.html')

@app.route('/users_list/')
def get_list_user():
    '''
    Функция возвращает список зарегистрированных пользователей.
    '''
    users = User.query.all()
    return render_template('list_user.html', users_list=users)

@app.route('/list_game/')
def get_list_game():
    '''
    Функция возвращает список игр.
    '''
    games = Game.query.all()
    return render_template('list_game.html', game_list=games)

@app.route('/list_game/<int:game_id>/')
def get_game(game_id):
    '''
    Функция возвращает информацию о конкретной игре.
    '''
    game = Game.query.get(game_id)
    if not game:
        return render_template('404.html'), 404

    ratings = Rating.query.filter_by(game_id=game_id).all()
    feedbacks = Feedback.query.filter_by(game_id=game_id).all()

    return render_template('game.html', game=game, ratings=ratings, feedbacks=feedbacks)

@app.route('/list_user/<int:user_id>/')
def get_user(user_id):
    '''
    Функция возвращает информацию о конкретном пользователе.
    '''
    user = User.query.get(user_id)
    if not user:
        return render_template('404.html'), 404
    ratings = Rating.query.filter_by(user_id=user_id).all()
    feedbacks = Feedback.query.filter_by(user_id=user_id).all()

    return render_template('user.html', user=user, ratings=ratings, feedbacks=feedbacks)



@app.route('/check_rating_entry/', methods=['GET', 'POST'])
def check_rating_entry():
    '''
    Функция возвращает форму для проверки налиция регистрации у пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при проверки пользователя на наличие
    регистрации.
    Если введенные данные не совпадаю с теми, что записаны в базе данных, то выводится ошибка с надписью:
    "Что-то пошло не так (( Попробуйте снова"
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = request.form.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        if user and username == user.username and password == user.password:
            session['user_id'] = user.id
            return redirect('/check_rating_entry/rating/')
        else:
            flash('Что-то пошло не так (( Попробуйте снова')
            return redirect(request.url)

    return render_template('rating_entry.html')

@app.route('/check_rating_entry/rating/', methods=['GET', 'POST'])
def rating_finish():
    '''
    Функция возвращает форму для оставления оценки.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную от пользователя при оставлении оценки.
    Если оценка у пользователя к игре уже есть, то оценка будет отредактирован.
    Если id игры нет в базе данные, выводится ошибка с надписью "Game not found".
    Если оценка выйдет из диапазона 0-10, то выведится ошибка.
    '''
    if request.method == 'POST':
        rating_int = request.form.get('rating_int')
        game_id = request.form.get('game_id')

        user_id = session.get('user_id')
        if user_id is None:
            return "User not found"

        game = Game.query.get(game_id)
        if game is None:
            return "Game not found"
        if int(rating_int) > 10:
            return "More 10"
        if int(rating_int) < 0:
            return "Less 0"

        existing_rating = Rating.query.filter_by(user_id=user_id, game_id=game_id).first()
        if existing_rating:
            existing_rating.score = rating_int
            db.session.commit()
        else:
            new_rating = Rating(user_id=user_id, game_id=game_id, score=rating_int)
            db.session.add(new_rating)
            db.session.commit()
        return render_template('finish_feedback.html')
    return render_template('rating.html')

@app.route('/check_feedback_entry/', methods=['GET', 'POST'])
def check_feedback_entry():
    '''
    Функция возвращает форму для проверки налиция регистрации у пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при проверки пользователя на наличие
    регистрации.
    Если введенные данные не совпадаю с теми, что записаны в базе данных, то выводится ошибка с надписью:
    "Что-то пошло не так (( Попробуйте снова"
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = request.form.get('user_id')

        user = User.query.filter_by(id=user_id).first()
        if user and username == user.username and password == user.password:
            session['user_id'] = user.id
            return redirect('/check_feedback_entry/feedback/')
        else:
            flash('Что-то пошло не так (( Попробуйте снова')
            return redirect(request.url)

    return render_template('feedback_entry.html')

@app.route('/check_feedback_entry/feedback/', methods=['GET', 'POST'])
def feedback_finish():
    '''
    Функция возвращает форму для оставления отзыва к игре.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную от пользователя при оставлении отзыва.
    Если отзыв у пользователя к игре уже есть, то отзыв будет отредактирован.
    Если id игры нет в базе данные, выводится ошибка с надписью "Game not found".
    '''
    if request.method == 'POST':
        feedback_user = request.form.get('feedback_user')
        game_id = request.form.get('game_id')

        user_id = session.get('user_id')
        if user_id is None:
            return "User not found"

        game = Game.query.get(game_id)
        if game is None:
            return "Game not found"

        existing_feedback = Feedback.query.filter_by(user_id=user_id, game_id=game_id).first()
        if existing_feedback:
            existing_feedback.feedback_user = feedback_user
            db.session.commit()
        else:
            new_feedback = Feedback(user_id=user_id, game_id=game_id, feedback_user=feedback_user)
            db.session.add(new_feedback)
            db.session.commit()

        return render_template('finish_feedback.html')

    return render_template('feedback.html')


admin = Admin(app, name='My Admin', template_mode='bootstrap3')

admin.add_view(ModelView(Rating, db.session))
admin.add_view(ModelView(Feedback, db.session))
admin.add_view(ModelView(Game, db.session))
admin.add_view(ModelView(User, db.session))


if __name__ == '__main__':
    app.run(debug=True)

