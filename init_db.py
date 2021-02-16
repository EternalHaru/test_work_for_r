#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import Config
from models.base import Base
from models.user import User


def init_db():
    engine = create_engine(Config().SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    db_session_manager = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session_manager.query_property()
    Base.metadata.create_all(bind=engine)
    test_user = User('test_user')
    test_user.hash_password('test_password')
    db_session_manager.add(test_user)
    db_session_manager.commit()


if __name__ == '__main__':
    init_db()
