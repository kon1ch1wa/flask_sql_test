import flask
from flask import Flask, redirect, render_template, request, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from models import Member, Info, db, Organization
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/nsdap'
db.init_app(app)
with app.app_context():
    db.create_all()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in flask.request.headers:
            token = flask.request.headers['x-access-token']
        if not token:
            return {'message': 'Token is missing !!'}, 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_member = Member.query \
                .filter_by(id=data['id']) \
                .first()
        except:
            return {'message': 'Token is invalid !!'}, 401
        # returns the current logged-in users contex to the routes
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/<int:ticket>')
def home(ticket):
    try:
        person = Member.query.filter_by(id=ticket).first()
        if person is None:
            raise KeyError
    except KeyError:
        return render_template('invalid.html')
    return render_template('home.html', name=person.name, surname=person.surname,
                           sub=person.subscription, ticket=ticket)


@app.route('/<int:ticket>')
def guest(ticket):
    try:
        person = Member.query.filter_by(id=ticket).first()
        if person is None:
            raise KeyError
    except KeyError:
        return render_template('invalid.html')
    return render_template('guest.html', name=person.name, surname=person.surname)


@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            with app.app_context():
                check_name = request.form.get('name')
                check_surname = request.form.get('surname')
                check_mail = request.form.get('email')
                check_pass = request.form.get('password')
                if request.form.get('sub'):
                    check_sub = True
                else:
                    check_sub = False
                if check_name == '' or check_surname == '' or check_mail == '' or check_pass == '':
                    raise ValueError

                hashed_pass = generate_password_hash(check_pass)
                new_member = Member(
                    name=check_name,
                    surname=check_surname,
                    email=check_mail,
                    pswd=hashed_pass,
                    subscription=check_sub,
                    connected=True
                )
                db.session.add(new_member)
                db.session.commit()
                return redirect(url_for('home', ticket=new_member.id))
        except ValueError:
            return render_template('sign_in.html', error=1)
        except NameError:
            return render_template('sign_in.html', error=2)
        except:
            db.session.rollback()
            return render_template('sign_in.html', error=3)
    return render_template('sign_in.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            with app.app_context():
                ticket = request.form['ticket']
                password = request.form['password']
                person = Member.query.filter_by(id=ticket).first()
                if person is None:
                    raise NameError

                if check_password_hash(person.password, password):
                    return redirect(url_for('home', ticket=ticket))
                else:
                    raise KeyError
        except NameError:
            return render_template('login.html', error=1)
        except KeyError:
            return render_template('login.html', error=2)
    return render_template('login.html')


# Only POST registration and authorization
@app.route('/post/reg', methods=['POST'])
def post_reg():
    try:
        name = flask.request.json['name']
        surname = flask.request.json['surname']
        email = flask.request.json['email']
        pswd = flask.request.json['pswd']
        sub = flask.request.json['sub']
        connected = flask.request.json['connected']
    except KeyError:
        flask.abort(400)
        return
    if any(map(lambda s: s == '', [name, surname, email, pswd, sub, connected])):
        flask.abort(400)
        return
    member = Member(
        name=name,
        surname=surname,
        email=email,
        pswd=pswd,
        subscription=sub,
        connected=connected
    )
    member.hash_pass()
    db.session.add(member)
    db.session.commit()
    return member.json


@app.route('/post/info', methods=['POST'])
@token_required
def post_info():
    try:
        phone = flask.request.json['phone']
        land = flask.request.json['land']
        city = flask.request.json['city']
        workplace = flask.request.json['workplace']
        partyTicket = flask.request.json['partyTicket']
    except KeyError:
        flask.abort(400)
        return
    info = Info(
        phone=phone,
        land=land,
        city=city,
        workplace=workplace,
        partyTicket=partyTicket
    )
    db.session.add(info)
    db.session.commit()
    return info.json


@app.route('/post/org', methods=['POST'])
@token_required
def post_org():
    try:
        org_name = flask.request.json['org_name']
        org_desc = flask.request.json['org_desc']
        employees_amount = flask.request.json['empl_amount']
    except KeyError:
        flask.abort(400)
        return
    org = Organization(
        org_name=org_name,
        org_desc=org_desc,
        employees_amount=employees_amount
    )
    db.session.add(org)
    db.session.commit()
    return org.json


@app.route('/post/login', methods=['POST'])
def post_login():
    handle = flask.request.json

    return flask.make_response()


if __name__ == "__main__":
    app.run(debug=True)
