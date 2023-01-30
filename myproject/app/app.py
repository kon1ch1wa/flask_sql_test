from werkzeug.security import generate_password_hash
from flask import Flask, url_for, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/nsdap'
db = SQLAlchemy(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Integer, nullable=False)


class MemberStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    subscription = db.Column(db.Boolean)

    partyTicket = db.Column(db.Integer, db.ForeignKey('member.id'))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            hashed_pass = generate_password_hash(request.form['password'])
            new_member = Member(
                name=request.form['name'],
                surname=request.form['surname'],
                password=hashed_pass
            )
            db.session.add(new_member)
            db.session.flush()

            new_member_status = MemberStatus(
                mail=request.form['email'],
                subscription=request.form['subscription'],
                partyTicket=new_member.id
            )
            db.session.add(new_member_status)
            db.session.commit()
        except:
            db.session.rollback()
            print('Database error: Connection Error')
    return render_template('sign_in.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            new_hashed_pass = generate_password_hash(request.form['password'])
            db_pass = db.Query.filter_by(password=new_hashed_pass).first()
            if new_hashed_pass != db_pass:
                raise KeyError
        except KeyError:
            return render_template('login_error.html')
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
