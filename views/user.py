from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError
from flask import abort

from models.product_group import ProductGroup
from models.user import User

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)
parser.add_argument('product_group_ids', type=int, action='append', required=False)


class DIServices(di_cnt.DeclarativeContainer):
    db_session_manager = di_prv.Provider()
    logger = di_prv.Provider()


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        username = data['username']
        password = data['password']
        product_group_ids = data.get('product_group_ids')
        product_groups = []

        if product_group_ids:
            for identifier in product_group_ids:
                product_group = ProductGroup.query.filter_by(id=identifier).first()
                if not product_group:
                    return {'msg': 'One of the product groups does not exist'}, 400
                else:
                    if not product_group.is_child_of(product_group_ids):
                        product_groups.append(product_group)

        if username is None or password is None:
            abort(400)

        if User.query.filter_by(username=username).first() is not None:
            return {'msg': 'User already exists'}, 400

        user = User(username=username)
        user.hash_password(password)
        user.available_product_groups.extend(product_groups)

        try:
            DIServices.db_session_manager().add(user)
            DIServices.db_session_manager().commit()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                       'msg': 'User {} was created'.format(data['username']),
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 201
        except SQLAlchemyError as e:
            DIServices.logger().error(str(e))
            return {'msg': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = User.query.filter_by(username=data['username']).first()

        if not current_user:
            return {'msg': "User {} doesn't exist".format(data['username'])}

        if current_user.verify_password(data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'msg': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'msg': 'Wrong credentials'}


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return {'access_token': access_token}
