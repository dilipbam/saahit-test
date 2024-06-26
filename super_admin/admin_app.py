import flask
from flask_jwt_extended import JWTManager
from flask import g
from super_admin.callbacks import admin_views, auth_views
from super_admin.utils.db_getter import get_session
from utilities.encoders import DobatoEncoder
from utilities.schemas.models import User

app = flask.Flask(__name__)
app.json = DobatoEncoder(app)
app.config['SECRET_KEY'] = 'sahashahit-consumer'
jwt_manager = JWTManager(app)
app.config['JWT_USER_CLAIM'] = 'identity'


@app.before_request
def before_request():
    g.db_session = get_session()


@app.teardown_request
def teardown_request(exception=None):
    session = g.pop('db_session', None)
    if session is not None:
        if exception is None:
            session.commit()
        else:
            session.rollback()
        session.remove()


def user_loader_callback(jwt_header, jwt_payload):
    identity = jwt_payload["sub"]
    user = g.db_session.get(User, identity)
    return user


jwt_manager.user_lookup_loader(user_loader_callback)

# jwt_manager.additional_claims_callback(user_claims_callback)

app.add_url_rule('/admin-api/login', view_func=auth_views.Login.as_view('login'))
app.add_url_rule('/admin-api/logout', view_func=auth_views.Logout.as_view('logout'))
app.add_url_rule('/admin-api/refresh-token', view_func=auth_views.RefreshTokenApi.as_view('refresh-token'))
app.add_url_rule('/admin-api/site', view_func=admin_views.ListRegisteredTables.as_view('db-table-list')),
app.add_url_rule('/admin-api/site/<table_name>', view_func=admin_views.ListTableData.as_view('user-lists'))
app.add_url_rule('/admin-api/site/add/<table_name>', view_func=admin_views.AddItem.as_view('add-data'))
app.add_url_rule('/admin-api/site/<table_name>/<int:item_id>',
                 view_func=admin_views.ItemDetail.as_view('item-details'), methods=['get', 'put', 'delete'])

if __name__ == '__main__':
    app.run(debug=True, port=9003)
