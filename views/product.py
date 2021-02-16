from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from models.product_group import ProductGroup
from models.product import Product
from models.user import User

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv

parser = reqparse.RequestParser()
parser.add_argument('product_group_id', type=int, required=False)
parser.add_argument('product_id', type=int, required=False)
parser.add_argument('group_id', type=int, required=False)
parser.add_argument('title', type=str, required=False)


class DIServices(di_cnt.DeclarativeContainer):
    db_session_manager = di_prv.Provider()


class ProductView(Resource):
    @jwt_required()
    def get(self, product_id=None):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        data = parser.parse_args()
        group_id = data.get('group_id')

        if not current_user.has_group_rights(group_id) or not current_user.has_product_rights(product_id):
            return {}, 403

        if group_id:
            product_group = ProductGroup.query.filter_by(id=group_id).all()
            products = product_group.get_nested_products()
        elif product_id:
            products = Product.query.filter_by(id=product_id).all()
        else:
            if len(current_user.available_product_groups) == 0:
                products = Product.query.all()
            else:
                products = []
                for group in current_user.available_product_groups:
                    z = group.get_nested_products()
                    products.extend(z)

        return [product.to_dict() for product in products]

    @jwt_required()
    def post(self):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        data = parser.parse_args()
        title = data.get('title')
        product_group_id = data.get('product_group_id')

        if not product_group_id:
            return {'msg': 'product_group_id required parameter'}, 400

        if not ProductGroup.query.filter_by(id=product_group_id).first():
            return {'msg': 'Product group does not exist'}, 400

        if not current_user.has_group_rights(product_group_id):
            return {}, 403

        new_product = Product(title, product_group_id)
        DIServices.db_session_manager().add(new_product)
        DIServices.db_session_manager().commit()

        return new_product.to_dict(), 201

    @jwt_required()
    def put(self, product_id=None):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if not product_id:
            return {'msg': 'Product does not exist'}, 400

        data = parser.parse_args()
        title = data.get('title')
        product_group_id = data.get('product_group_id')

        if not product_group_id:
            return {'msg': 'product_group_id required'}, 400

        if not current_user.has_group_rights(product_group_id) or not current_user.has_product_rights(product_id):
            return {}, 403

        if not ProductGroup.query.filter_by(id=product_group_id).first():
            return {'msg': 'Product group does not exist'}, 400

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return {'msg': 'Product does not exist'}, 400

        product.title = title
        product.product_group_id = product_group_id
        DIServices.db_session_manager().add(product)
        DIServices.db_session_manager().commit()

        return product.to_dict(), 200

    @jwt_required()
    def delete(self, product_id):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if not current_user.has_product_rights(product_id):
            return {}, 403

        if product := Product.query.filter_by(id=product_id).first():
            DIServices.db_session_manager().delete(product)
            DIServices.db_session_manager().commit()
            return {'msg': 'Group deleted successfully'}, 204
        else:
            return {'msg': 'Product does not exist'}, 400
