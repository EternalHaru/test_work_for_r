from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
import bcrypt

from models.product_group import ProductGroup
from models.product import Product
from models.base import Base

rights_table = Table('user_product_group', Base.metadata,
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('product_group_id', Integer, ForeignKey('product_group.id'))
                     )


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    available_product_groups = relationship("ProductGroup", secondary=rights_table)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def hash_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def has_group_rights(self, *groups_ids):
        for group_id in groups_ids:
            if not group_id:
                continue
            product_group = ProductGroup.query.filter_by(id=group_id).first()
            if not product_group:
                return False
            if not (group_id in [group.id for group in self.available_product_groups]) \
                    and not product_group.is_child_of([group.id for group in self.available_product_groups]):
                return False

        return True

    def has_product_rights(self, *products_ids):
        for product_id in products_ids:
            if not product_id:
                continue
            product = Product.query.filter_by(id=product_id).first()
            if not product:
                return False
            if not self.has_group_rights(product.product_group_id):
                return False

        return True

    def normalize_rights(self):
        product_groups = []
        product_group_ids = [group.id for group in self.available_product_groups]
        for right in self.available_product_groups:
            product_group = ProductGroup.query.filter_by(id=right.id).first()
            if not product_group.is_child_of(product_group_ids):
                product_groups.append(product_group)

        self.available_product_groups = product_groups
