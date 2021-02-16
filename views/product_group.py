from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from models.product_group import ProductGroup
from models.user import User

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv

parser = reqparse.RequestParser()
parser.add_argument('children', type=dict, action='append', required=False, default=[])
parser.add_argument('product_group_id', type=int, required=False)
parser.add_argument('parent_id', type=int, required=False)
parser.add_argument('title', type=str, required=False, default='')


class DIServices(di_cnt.DeclarativeContainer):
    db_session_manager = di_prv.Provider()


class ProductGroupView(Resource):
    @jwt_required()
    def get(self, product_group_id=None):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if product_group_id:
            if current_user.has_group_rights(product_group_id):
                product_group_tree = ProductGroup.query.filter_by(id=product_group_id).all()
            else:
                return {}, 403
        else:
            if len(current_user.available_product_groups) == 0:
                product_group_tree = ProductGroup.query.filter_by(parent_id=None).all()
            else:
                product_group_tree = current_user.available_product_groups

        return [group.to_dict() for group in product_group_tree]

    def _save(self, title, parent_id, children):
        new_product_group = ProductGroup(title)
        new_product_group.parent_id = parent_id

        DIServices.db_session_manager().add(new_product_group)
        DIServices.db_session_manager().commit()

        for child in children:
            self._save(child.get('title'), new_product_group.id, child.get('children'))

        return new_product_group

    @jwt_required()
    def post(self, product_group_id=None):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        data = parser.parse_args()
        title = data.get('title')
        parent_id = data.get('parent_id')
        children = data.get('children')

        if parent_id:
            if not current_user.has_group_rights(parent_id):
                return {}, 403

        if parent_id and not ProductGroup.query.filter_by(id=parent_id).first():
            return {'msg': 'Branch parent does not exist'}, 400

        new_product_group = self._save(title, parent_id, children)

        if not parent_id:
            current_user.available_product_groups.append(new_product_group)

        current_user.normalize_rights()
        DIServices.db_session_manager().add(current_user)
        DIServices.db_session_manager().commit()

        return new_product_group.to_dict(), 201

    @jwt_required()
    def put(self, product_group_id):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        data = parser.parse_args()
        title = data.get('title')
        parent_id = data.get('parent_id')
        children = data.get('children')

        if not current_user.has_group_rights(product_group_id, parent_id):
            return {}, 403

        product_group = ProductGroup.query.filter_by(id=product_group_id).first()

        if not product_group:
            return {'msg': 'Group does not exist'}, 400

        if parent_id and not ProductGroup.query.filter_by(id=parent_id).first():
            return {'msg': 'Branch parent does not exist'}, 400

        product_group.title = title
        product_group.parent_id = parent_id
        product_group.children.delete()

        DIServices.db_session_manager().add(product_group)
        DIServices.db_session_manager().commit()

        for child in children:
            self._save(child.get('title'), product_group.id, child.get('children'))

        if not parent_id:
            current_user.available_product_groups.append(product_group)

        current_user.normalize_rights()
        DIServices.db_session_manager().add(current_user)
        DIServices.db_session_manager().commit()

        return product_group.to_dict(), 200

    @jwt_required()
    def delete(self, product_group_id):
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if not current_user.has_group_rights(product_group_id):
            return {}, 403

        if product_group := ProductGroup.query.filter_by(id=product_group_id).first():
            DIServices.db_session_manager().delete(product_group)
            DIServices.db_session_manager().commit()
            return {'msg': 'Group deleted successfully'}, 204
        else:
            return {'msg': 'Group does not exist'}, 400
