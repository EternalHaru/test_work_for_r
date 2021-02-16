from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from models.base import Base


class ProductGroup(Base):
    __tablename__ = "product_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('product_group.id', ondelete='CASCADE'), nullable=True)
    children = relationship(
        "ProductGroup",
        backref=backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade="all, delete")

    def __init__(self, title):
        super().__init__()
        self.title = title

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'parent_id': self.parent_id if self.parent else None,
            'children': [child.to_dict() for child in self.children],
            'products': [product.to_dict() for product in self.products]
        }

    def get_nested_products(self):
        products = self.products[:]
        for elem in [child.get_nested_products() if child.children else [] for child in self.children]:
            products.extend(elem)

        return products

    def is_child_of(self, groups_id):
        parents = []
        parent = self.parent
        if parent:
            parents.append(parent.id)
        while parent:
            parent = parent.parent
            if parent:
                parents.append(parent.id)

        if set(groups_id).intersection(set(parents)):
            return True

        return False
