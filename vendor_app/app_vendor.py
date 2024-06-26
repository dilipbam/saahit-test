
import flask
from flask import Flask, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utilities.encoders import DobatoEncoder
from vendor_app.callbacks import user_views, venue_views
from utilities.db_getter import get_session
from utilities.schemas.models import User


app = flask.Flask(__name__)
app.json = DobatoEncoder(app)
app.config['SECRET_KEY'] = 'sahashahit-vendor'
jwt_manager = JWTManager(app)
app.config['JWT_USER_CLAIM'] = 'identity'

CORS(app)
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

app.add_url_rule('/vendor-api/register', view_func=user_views.Register.as_view('register'))
app.add_url_rule('/vendor-api/verify-email', view_func=user_views.VerifyEmail.as_view('verify-email'))
app.add_url_rule('/vendor-api/login', view_func=user_views.VendorLogin.as_view('login'))
app.add_url_rule('/vendor-api/logout', view_func=user_views.VendorLogout.as_view('logout'))
app.add_url_rule('/vendor-api/refresh-token', view_func=user_views.RefreshTokenApi.as_view('refresh-token'))
app.add_url_rule('/vendor-api/forgot-password', view_func=user_views.ForgotPassword.as_view('forgot-password'))
app.add_url_rule('/vendor-api/reset-password/<token>', view_func=user_views.ResetPassword.as_view('rest-password'))
app.add_url_rule('/vendor-api/resend-otp', view_func=user_views.ResendOTP.as_view('resend-otp'))

app.add_url_rule('/vendor-api/profile', view_func=user_views.VendorProfileApi.as_view('profile'))
app.add_url_rule('/vendor-api/basic-info', view_func=user_views.VendorBasicInfoApi.as_view('vendor-basic-info'))

app.add_url_rule('/vendor-api/profile-detail',
                 view_func=user_views.VendorProfileDetailApi.as_view('vendor-profile-detail-api'))

app.add_url_rule('/vendor-api/vendor-industry-list',
                 view_func=venue_views.VendorIndustryList.as_view('vendor-industry-list-api'))

# app.add_url_rule('/vendor-api/update-profile',
#                  view_func=user_views.UpdateVendorProfile.as_view('update-vendor-profile'))

app.add_url_rule('/vendor-api/venue', view_func=venue_views.VenueListApi.as_view('venue-list-api'))
app.add_url_rule('/vendor-api/venue/<int:venue_id>', view_func=venue_views.VenueDetailApi.as_view('venue-detail-api'))
app.add_url_rule('/vendor-api/venue/<int:venue_id>/venue-space',
                 view_func=venue_views.VenueSpaceListApi.as_view('venue-space-list'))

app.add_url_rule('/vendor-api/venue/<int:venue_id>/venue-space/<int:space_id>',
                 view_func=venue_views.VenueSpaceDetailApi.as_view('venue-space-detail'))

app.add_url_rule('/vendor-api/menu',
                 view_func=venue_views.MenuListApi.as_view('menu-list'))

app.add_url_rule('/vendor-api/menu/<int:menu_id>',
                 view_func=venue_views.MenuDetailApi.as_view('menu-detail-api'))

app.add_url_rule('/vendor-api/food-items',
                 view_func=venue_views.FoodItemListApi.as_view('food-items-list-api'))
app.add_url_rule('/vendor-api/food-items/<int:item_id>',
                 view_func=venue_views.FoodItemDetailApi.as_view('food-item-detail-api'))
app.add_url_rule('/vendor-api/menu/<int:menu_id>/menu-items',
                 view_func=venue_views.MenuFoodItemApi.as_view('menu-food-item-api'))
app.add_url_rule('/vendor-api/menu/<int:menu_id>/menu-items/<int:menu_food_item_id>',
                 view_func=venue_views.MenuFoodItemDetailApi.as_view('menu-food-item-detail-api'))

if __name__ == '__main__':
    app.run(debug=True, port=9001)
