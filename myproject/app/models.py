from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    pswd = db.Column(db.String(102), nullable=False)
    subscription = db.Column(db.Boolean, default=False)
    connected = db.Column(db.Boolean, default=False)

    info = db.relationship('Info', back_populates='member', uselist=False)
    org = db.relationship('Organization', back_populates='leader', uselist=False)
    corp = db.relationship('Corporation', back_populates='leader', uselist=False)

    def hash_pass(self):
        self.pswd = generate_password_hash(self.pswd)

    def check_hash(self, password):
        return check_password_hash(self.pswd, password)

    def __repr__(self):
        return f'Member:\t{self.name} {self.surname}\t{self.id}'

    @property
    def json(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "info": [one_info.json for one_info in self.info],
            "subscription": self.subscription,
            "connected": self.connected
        }


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription = db.Column(db.Boolean, default=False)
    connected = db.Column(db.Boolean, default=False)

    member = db.relationship('Member', back_populates='status')

    @property
    def json(self):
        return {
            "id": self.id,
            "subscription": self.subscription,
            "connected": self.connected
        }


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(100), nullable=False, unique=True)
    land = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    workplace = db.Column(db.String(100), nullable=False, default='Unemployed')
    partyTicket = db.Column(db.Integer, db.ForeignKey('member.id'))

    member = db.relationship('Member', back_populates='info', uselist=False)
    organizations = db.relationship('Organization', back_populates='org')

    @property
    def json(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "land": self.land,
            "city": self.city,
            "workplace": self.workplace,
            "partyTicket": self.partyTicket
        }


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(100), nullable=False, unique=True)
    org_desc = db.Column(db.Text, nullable=False)
    employees_amount = db.Column(db.Integer, nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    leader = db.relationship('Member', back_populates='org', uselist=False)

    @property
    def json(self):
        return {
            "id": self.id,
            "org_name": self.org_name,
            "org_desc": self.org_desc,
            "employees_amount": self.employees_amount,
            "leader_id": self.leader_id
        }


class Corporation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    gdp = db.Column(db.Integer)
    influence = db.Column(db.Integer)
    employees = db.Column(db.Integer)

    leaders = db.relationship('Member', back_populates='corp')

    @property
    def json(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "category": self.category,
            "gdp": self.gdp,
            "influence": self.influence,
            "employees": self.employees,
            "leaders": [leader.json for leader in self.leaders]
        }