from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, url_for, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/nsdap'
db = SQLAlchemy(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(102), nullable=False)

    def __repr__(self):
        return f'Member:\t {self.name}\t {self.surname}\t #{self.id}\n'


class MemberStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    subscription = db.Column(db.Boolean)

    partyTicket = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'E-mail and Party Ticket:\t {self.mail}\t {self.partyTicket}\n' \
               f'Subscription Status:\t {self.subscription}\n'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/<int:ticket>')
def home(ticket):
    try:
        person = Member.query.filter_by(id=ticket).first()
        if person is None:
            raise KeyError
        person_stat = MemberStatus.query.filter_by(partyTicket=ticket).first()
    except KeyError:
        return render_template('invalid.html')
    return render_template('home.html', name=person.name, surname=person.surname,
                           sub=person_stat.subscription, ticket=ticket)


@app.route('/<int:ticket>')
def guest():
    return render_template('guest.html')


@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            with app.app_context():
                check_name = request.form.get('name')
                check_surname = request.form.get('surname')
                check_mail = request.form.get('email')
                check_pass = request.form.get('password')
                check_sub = False
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
                    password=hashed_pass
                )
                db.session.add(new_member)
                db.session.commit()

                new_member_status = MemberStatus(
                    mail=check_mail,
                    subscription=check_sub,
                    partyTicket=new_member.id
                )
                db.session.add(new_member_status)
                db.session.commit()

                return redirect(url_for('home', ticket=new_member_status.partyTicket))
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


if __name__ == "__main__":
    app.run(debug=True)
