#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Product, ProductGroup, Base
from config import Config
from init_db import init_db
import csv


def load_from_csv():
    engine = create_engine(Config().SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    with open('example.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            r = [it.strip().lower() for it in row]
            levels = r[:-1]
            item = r[-1]
            prev_product_group = None
            if not Product.query.filter_by(title=item).first():
                for level in levels:
                    product_group = ProductGroup.query.filter_by(title=level).first()
                    if not product_group:
                        product_group = ProductGroup(level)
                        if prev_product_group:
                            product_group.parent_id = prev_product_group.id
                        db_session.add(product_group)
                        db_session.commit()
                    prev_product_group = product_group
                new_product = Product(item, prev_product_group.id)
                db_session.add(new_product)
                db_session.commit()


if __name__ == '__main__':
    init_db()
    load_from_csv()
