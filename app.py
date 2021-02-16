#!/usr/bin/env python3
import os

from flask import Flask
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_jwt_extended import JWTManager

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv


from config import Config
from models import Base
from views import user, product_group, product

config = Config()

app = Flask(os.path.join(os.path.dirname(os.path.abspath('__file__')), 'app'))
app.config.from_object(config)
jwt = JWTManager(app)
api = Api(app)

# DB session config
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session_manager = scoped_session(sessionmaker(bind=engine))
Base.query = db_session_manager.query_property()


class DIServices(di_cnt.DeclarativeContainer):
    db_session_manager = di_prv.Object(db_session_manager)
    logger = di_prv.Object(app.logger)


user.DIServices.override(DIServices)
product_group.DIServices.override(DIServices)
product.DIServices.override(DIServices)


api.add_resource(user.UserRegistration, '/registration')
api.add_resource(user.UserLogin, '/login')
api.add_resource(user.TokenRefresh, '/token/refresh')

api.add_resource(product_group.ProductGroupView, '/product_groups', '/product_groups/<int:product_group_id>')
api.add_resource(product.ProductView, '/products', '/products/<int:product_id>')


@app.before_first_request
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session_manager.remove()


if __name__ == '__main__':
    app.run()
