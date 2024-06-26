import flask
from flask import g
from flask_jwt_extended import JWTManager

from customer_app.callbacks import user_views, vendor_views
from utilities.db_getter import get_session
from flask_cors import CORS

from utilities.encoders import DobatoEncoder
from utilities.schemas.models import User


app = flask.Flask(__name__)
app.json = DobatoEncoder(app)
app.config['SECRET_KEY'] = 'sahashahit-consumer'
jwt_manager = JWTManager(app)
app.config['JWT_USER_CLAIM'] = 'identity'

CORS(app)
session = get_session()

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

app.add_url_rule('/consumer-api/register', view_func=user_views.Register.as_view('register'))
app.add_url_rule('/consumer-api/verify-email', view_func=user_views.VerifyEmail.as_view('verify-email'))
app.add_url_rule('/consumer-api/resend-otp', view_func=user_views.ResendOTP.as_view('resend-otp'))
app.add_url_rule('/consumer-api/login', view_func=user_views.Login.as_view('login'))
app.add_url_rule('/consumer-api/logout', view_func=user_views.Logout.as_view('logout'))
app.add_url_rule('/consumer-api/profile', view_func=user_views.CustomerProfile.as_view('profile'))
app.add_url_rule('/consumer-api/refresh-token', view_func=user_views.RefreshTokenApi.as_view('refresh-token'))
app.add_url_rule('/consumer-api/forgot-password', view_func=user_views.ForgotPassword.as_view('forgot-password'))
app.add_url_rule('/consumer-api/reset-password/<token>', view_func=user_views.ResetPassword.as_view('rest-password'))
app.add_url_rule('/consumer-api/update-profile/<int:user_id>',view_func=user_views.UpdateProfile.as_view('update-profile'))
app.add_url_rule('/consumer-api/vendor-industry-list',
                 view_func=vendor_views.VendorIndustryList.as_view('vendor-industry-list'))
app.add_url_rule('/consumer-api/venues-list', view_func=vendor_views.VenueList.as_view('venue-list'))
app.add_url_rule('/consumer-api/venue-detail/<int:vendor_profile_id>',
                 view_func=vendor_views.VenueDetail.as_view('venue-detail'))
app.add_url_rule('/consumer-api/menu-list/<int:vendor_profile_id>',
                 view_func=vendor_views.VendorMenuList.as_view('vendor-menu'))
app.add_url_rule('/consumer-api/menu-list/<int:vendor_profile_id>/food-items/<int:menu_id>',
                 view_func=vendor_views.VendorMenuDetail.as_view('vendor-menu-detail'))

if __name__ == '__main__':
    app.run(debug=True, port=9002)