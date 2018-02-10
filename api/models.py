# models
import os
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import JSON, TEXT, TypeDecorator
from datetime import datetime

class StringyJSON(TypeDecorator):
    """Stores and retrieves JSON as TEXT."""

    impl = TEXT

    def process_bind_param(self, value, dialect):
        """Map value into json data."""
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """Map json data to python dictionary."""
        if value is not None:
            value = json.loads(value)
        return value


# TypeEngine.with_variant says "use StringyJSON instead when
# connecting to 'sqlite'"
MagicJSON = JSON().with_variant(StringyJSON, 'sqlite')

type_map = {'sqlite': MagicJSON, 'postgresql': JSON}
json_type = type_map[os.getenv("DB_TYPE")]

db = SQLAlchemy()

class ModelViewsMix(object):
    def save(self):
        """Saves an instance of the model to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            db.session.rollback()
            return error
    
    def delete(self):
        """Delete an instance of the model from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            db.session.rollback()
            return error


class User(db.Model, ModelViewsMix):
    
    __tablename__ = 'User'

    id = db.Column(db.String, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    image_url = db.Column(db.String)
    authorization_code = db.Column(db.String, unique=True)
    authorization_code_status = db.Column(db.Boolean, default=False)
    wallet = db.relationship('Wallet', backref='user', lazy='dynamic')
    transaction = db.relationship('Transaction', backref='user', lazy='dynamic')
    notification = db.relationship('Notification', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<User %r %r>' % (self.firstname, self.lastname)


class Wallet(db.Model, ModelViewsMix):
    
    __tablename__ = 'Wallet'

    id = db.Column(db.String, primary_key=True)
    wallet_amount =  db.Column(db.Float, default=0.00)
    transaction = db.relationship('Transaction', backref='wallet', lazy='dynamic')
    user_id = db.Column(db.String(), db.ForeignKey('User.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Wallet %r %r>' % (self.user_id, self.wallet_amount)


class Transaction(db.Model, ModelViewsMix):
    
    __tablename__ = 'Transaction'

    id = db.Column(db.String, primary_key=True)
    transaction_detail = db.Column(db.String, nullable=False)
    type_of_operation = db.Column(db.String, nullable=False)
    cost_of_transaction = db.Column(db.Float, default=0.00)
    amount_before_transaction = db.Column(db.Float, default=0.00)
    amount_after_transaction = db.Column(db.Float, default=0.00)
    paystack_deduction = db.Column(db.Float, default=0.00)
    user_id = db.Column(db.String(), db.ForeignKey('User.id'))
    sender_id = db.Column(db.String(), db.ForeignKey('User.id'))
    user_wallet_id = db.Column(db.String(), db.ForeignKey('Wallet.id'))
    sender_wallet_id = db.Column(db.String(), db.ForeignKey('Wallet.id'))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Transaction %r %r>' % (self.user_id, self.transaction_detail)


class Notification(db.Model, ModelViewsMix):
    
    __tablename__ = 'Notification'

    id = db.Column(db.String, primary_key=True)
    message = db.Column(db.String)
    recipient_id = db.Column(db.String(), db.ForeignKey('User.id'))
    sender_id = db.Column(db.String(), db.ForeignKey('User.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Transaction %r %r>' % (self.message)
