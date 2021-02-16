from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from models.base import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    product_group_id = Column(Integer, ForeignKey('product_group.id'), nullable=False)
    product_group = relationship("ProductGroup", backref=backref('products', cascade="all,delete"))

    def __init__(self, title, product_group_id):
        super().__init__()
        self.title = title
        self.product_group_id = product_group_id

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'product_group_id': self.product_group_id
        }
