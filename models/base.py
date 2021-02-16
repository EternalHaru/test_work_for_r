import re

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:

    def __init__(self):
        pass

    @declared_attr
    def __tablename__(cls):
        return re.sub('(?!^)([A-Z][a-z]+)', r'_\1', cls.__name__).lower()
