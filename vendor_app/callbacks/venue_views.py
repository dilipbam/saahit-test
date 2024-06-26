from flask import request
from marshmallow import validate
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from vendor_app.callbacks.user_validators import SpacesSchema, VenueSchema, MenuSchema, FoodItemSchema, MenuItemSchema

from vendor_app.utils.authentication_utils import load_current_user

from utilities.responses import *
from utilities.dobato import DobatoApi  # TODO: change to dobato api for vendors as well

from utilities.schemas.models import VendorProfile, Venue, FoodItem, VendorIndustry, Menu, MenuItemTable, \
    VenueSpace


class VenueListApi(DobatoApi):
    def post(self):
        """
        API endpoint to add new venue.

        Methods:
            post(): Handle POST requests for venue.

        Usage:
            Send a post request to '/vendor-api/venue' with logged-in user and venue data
            containing 'venue_name', 'location', 'parking_capacity', 'venue_type', 'mandatory_catering'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        data = request.get_json()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        # vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        # if not vendor_profile:
        #     return bad_request_error(msg="Vendor Profile doesn't exists")

        venue = (self.db.query(Venue).
                 join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id).
                 filter(VendorProfile.user_id == user.id).first())
        if venue:
            return bad_request_error(msg="Venue already exists")

        venue_industry = self.db.query(VendorIndustry).filter_by(industry_name='Venue').first().id
        if vendor_profile.industry_id != venue_industry:
            return bad_request_error("Vendor not registered as a venue")

        # for industry id if not sent in request by frontend
        # if vendor_type_id:
        #     industry_id = vendor_profile.industry_id
        data['industry_id'] = vendor_profile.industry_id
        venue_schema = VenueSchema()

        try:
            validated_data = venue_schema.load(data)
            validated_data['vendor_profile_id'] = vendor_profile.id
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            new_venue = Venue(**validated_data)
            self.db.add(new_venue)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(e)
            return bad_request_error(msg="Couldn't add venue")
        finally:
            self.db.close()
        return success_response(msg='Venue Added successfully')

    def get(self):
        """
        API endpoint to get the user's venue.

        Methods:
            get(): Handle GET requests to get the venue.

        Usage:
            Send a get request to '/vendor-api/venue' with logged-in user

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        venue = (self.db.query(Venue).
                 join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id).
                 filter(VendorProfile.user_id == user.id).all())
        rows = self.make_obj_serializable(venue)
        return self.list_response(rows)


class VenueDetailApi(DobatoApi):
    def get(self, venue_id):
        """
        API endpoint to get venue detail.

        Methods:
            get(): Handle get requests for a venue.

        Usage:
            Send a get request to '/vendor-api/venue/<venue_id>' with logged-in user.

        Returns:
            JSON response with venue data.
        """
        user = load_current_user()
        venue = (self.db.query(Venue).
                 join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id).
                 filter(and_(VendorProfile.user_id == user.id, Venue.id == venue_id)).first())

        if venue:
            rows = self.make_obj_serializable(venue)
            return self.detail_response(rows)
        else:
            return server_error(msg="No venue data")

    def put(self, venue_id):
        """
        API endpoint to update a venue.

        Methods:
            put(): Handle PUT requests for venue.

        Usage:
            Send a put request to '/vendor-api/venue/<venue_id>' with logged-in user and venue data
            containing 'venue_name', 'location', 'parking_capacity', 'venue_type', 'mandatory_parking'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        data = request.get_json()

        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified.")

        venue = (self.db.query(Venue).
                 join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id).
                 filter(and_(VendorProfile.user_id == user.id, Venue.id == venue_id)).first())

        if not venue:
            return not_found_error(msg="Venue doesn't exists")

        # vendor_type_id = self.get_vendor_type_id()
        # for industry id if not sent in request by frontend
        # if vendor_type_id:
        #     rows = self.db.query(VendorProfile).filter(VendorProfile.user_id == user.id).with_entities(
        #         VendorProfile.industry_id).first()
        #     industry_id = rows[0]

        data['industry_id'] = venue.industry_id
        venue_schema = VenueSchema()

        try:
            validated_data = venue_schema.load(data)
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            for key, value in validated_data.items():
                setattr(venue, key, value)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(e)
            return bad_request_error(msg="Couldn't update venue")
        finally:
            self.db.close()
        return success_response(msg='Venue Updated successfully')


class VenueSpaceListApi(DobatoApi):
    def get(self, venue_id):
        """
        API endpoint to get venue spaces.

        Methods:
            get(): Handle get requests for a venue spaces.

        Usage:
            Send a get request to '/vendor-api/venue/<venue_id>/venue-space' with logged-in user.

        Returns:
            JSON response with venue space data.
        """
        user = load_current_user()
        #TODO : check for logged in and valid user
        venue_space = (self.db.query(VenueSpace)
                       .join(Venue, Venue.id == VenueSpace.venue_id)
                       .filter(Venue.id == venue_id))
        data = venue_space.all()
        return self.list_response(data)

    def post(self, venue_id):
        """
        API endpoint to add new venue-space.

        Methods:
            post(): Handle POST requests for venue-space.

        Usage:
            Send a post request to '/vendor-api/venue/<int:venue_id>/venue-space' with logged-in user and venue data
            containing 'space_name', 'space_type', 'description', 'rate', 'type_of_charge', 'seating_capacity' and
            'floating_capacity'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()

        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        venue = self.db.query(Venue).filter_by(id=venue_id).first()
        if not venue:
            return forbidden_error(msg="Venue doesn't exists")
        # TODO: images model needs to be finalized to save images.

        data = request.get_json()
        spaces_schema = SpacesSchema()
        # try:
        #     rate = int(data.get('rate'))
        #     seating_capacity = int(data.get('seating_capacity'))
        #     floating_capacity = int(data.get('floating_capacity'))
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are integers.')
        #
        # data['rate'] = rate
        # data['seating_capacity'] = seating_capacity
        # data['floating_capacity'] = floating_capacity

        try:
            validated_data = spaces_schema.load(data)
            validated_data['venue_id'] = venue.id
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            space_obj = VenueSpace(**validated_data)
            self.db.add(space_obj)
            self.db.commit()
            return success_response(msg='Spaces added for venue successfully')
        except SQLAlchemyError as e:
            print(e)
            self.db.rollback()
            return server_error(msg='Cannot add venue space')
        finally:
            self.db.close()


class VenueSpaceDetailApi(DobatoApi):
    def get(self, venue_id, space_id):
        """
        API endpoint to get venue-space detail.

        Methods:
            get(): Handle get requests for a venue-space detail.

        Usage:
            Send a get request to '/vendor-api/venue/<int:venue_id>/venue-space/<int:space_id>' with logged-in user.

        Returns:
            JSON response with venue data.
        """
        user = load_current_user()
        space_detail = (self.db.query(VenueSpace)
                        .join(Venue, Venue.id == VenueSpace.venue_id)
                        .join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id)
                        .filter(VendorProfile.user_id == user.id)
                        .filter(VenueSpace.id == space_id)
                        .filter(Venue.id == venue_id))
        data = space_detail.first()
        if data:
            return self.detail_response(data)
        else:
            return not_found_error(msg="No data for this venue space")

    def put(self, venue_id, space_id):
        """
        API endpoint to update a venue-space.

        Methods:
            put(): Handle PUT requests for a venue-space.

        Usage:
            Send a put request to '/vendor-api/venue/<int:venue_id>/venue-space/<int:space_id>' with logged-in user
            and venue space data containing 'space_name', 'space_type, ''description', 'rate', 'type_of_charge',
            'seating_capacity' and 'floating_capacity'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        space = (self.db.query(VenueSpace)
                 .join(Venue, Venue.id == VenueSpace.venue_id)
                 .join(VendorProfile, VendorProfile.id == Venue.vendor_profile_id)
                 .filter(VendorProfile.user_id == user.id)
                 .filter(VenueSpace.id == space_id)
                 .filter(Venue.id == venue_id)).first()
        if not space:
            return forbidden_error(msg="Space doesn't exists")
        # TODO: images model needs to be finalized to save images.
        data = request.get_json()
        spaces_schema = SpacesSchema()

        # try:
        #     rate = int(data.get('rate'))
        #     seating_capacity = int(data.get('seating_capacity'))
        #     floating_capacity = int(data.get('floating_capacity'))
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are integers.')
        #
        # data['rate'] = rate
        # data['seating_capacity'] = seating_capacity
        # data['floating_capacity'] = floating_capacity

        try:
            validated_data = spaces_schema.load(data)
            validated_data['venue_id'] = venue_id
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            for key, value in validated_data.items():
                setattr(space, key, value)
            self.db.commit()
            return success_response(msg='Space details for venue updated successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot update venue space')
        finally:
            self.db.close()

    #pending
    def delete(self, venue_id, space_id):
        """
        API endpoint to delete a venue-space.

        Methods:
            delete(): Handle DELETE requests for a venue-space.

        Usage:
            Send a DELETE request to '/vendor-api/venue/<int:venue_id>/venue-space/<int:space_id>' with logged-in user

        Returns:
            JSON response with success message.
        """
        user_id = self.user.id
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user_id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        space = self.db.query(VenueSpace).filter_by(id=space_id, venue_id=venue_id)
        if not space.first():
            return forbidden_error(msg="Space doesn't exists")

        try:
            space.delete()
            self.db.commit()
            return success_response(msg='Space deleted successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot delete space')
        finally:
            self.db.close()


class MenuListApi(DobatoApi):
    #pass
    def post(self):
        """
        API endpoint to add new menu.

        Methods:
            post(): Handle POST requests for menu.

        Usage:
            Send a post request to '/vendor-api/menu' with logged-in user and data
            containing 'name', 'description', 'cuisine', 'no_of_items', 'rate'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        data = request.get_json()
        menu_schema = MenuSchema()

        if not user:
            return bad_request_error(msg="User doesn't exists")

        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error(msg="Vendor Profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        # try:
        #     rate = float(data.get('rate'))
        #     no_of_items = int(data.get('no_of_items'))
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are integers.')
        #
        # data['vendor_profile_id'] = vendor_profile.id
        # data['rate'] = rate
        # data['no_of_items'] = no_of_items
        try:
            validated_data = menu_schema.load(data)
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            new_data = Menu(**validated_data)
            self.db.add(new_data)
            self.db.commit()
            return success_response(msg='Menu added successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot add new menu')
        finally:
            self.db.close()

    def get(self):
        """
        API endpoint to get vendor menus.

        Methods:
            get(): Handle get requests for a vendor menus.

        Usage:
            Send a get request to '/vendor-api/menu' with logged-in user.

        Returns:
            JSON response with vendor menu data.
        """
        user = load_current_user()
        #TODO : need to check if user exists, plus if user is verified and vendor, i.e. check if current user is customer or vendor as well(recreate by sending empty bearer token)
        menu_data = (self.db.query(Menu)
                     .join(VendorProfile, VendorProfile.id == Menu.vendor_profile_id)
                     .filter(VendorProfile.user_id == user.id)
                     .filter(VendorProfile.id == Menu.vendor_profile_id)).all()

        if menu_data:
            return self.list_response(menu_data)
        else:
            return not_found_error(msg="No menu for this vendor")


class MenuDetailApi(DobatoApi):
    def get(self, menu_id):
        """
        API endpoint to get menu detail.

        Methods:
            get(): Handle get requests for a menu detail.

        Usage:
            Send a get request to '/vendor-api/menu/<int:menu_id>' with logged-in user.

        Returns:
            JSON response with venue data.
        """
        user = load_current_user()
        #TODO : need to check if user exists, plus if user is verified and vendor, i.e. check if current user is customer or vendor(recreate by sending empty bearer token)
        menu_detail = (self.db.query(Menu)
                       .join(VendorProfile, VendorProfile.id == Menu.vendor_profile_id)
                       .filter(VendorProfile.user_id == user.id)
                       .filter(Menu.id == menu_id))
        data = menu_detail.first()
        if data:
            return self.detail_response(data)
        else:
            return not_found_error(msg="No menu data for this vendor")

    #passed
    def put(self, menu_id):
        """
        API endpoint to update a menu.

        Methods:
            put(): Handle PUT requests for a menu.

        Usage:
            Send a put request to '/vendor-api/menu/<int:menu_id>' with logged-in user
            and menu data containing 'name', 'description', 'cuisine', 'no_of_items', 'rate'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        menu = (self.db.query(Menu)
                .join(VendorProfile, VendorProfile.id == Menu.vendor_profile_id)
                .filter(VendorProfile.user_id == user.id)
                .filter(Menu.id == menu_id)).first()
        if not menu:
            return forbidden_error(msg="Menu doesn't exists")

        data = request.get_json()
        menu_schema = MenuSchema()
        # try:
        #     rate = float(data.get('rate'))
        #     no_of_items = int(data.get('no_of_items'))
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are integers.')
        #
        # data['vendor_profile_id'] = menu.vendor_profile_id
        # data['rate'] = rate
        # data['no_of_items'] = no_of_items

        try:
            validated_data = menu_schema.load(data)
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            for key, value in validated_data.items():
                setattr(menu, key, value)
            self.db.commit()
            return success_response(msg='Menu updated for venue successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot update menu')
        finally:
            self.db.close()

    def delete(self, menu_id):
        """
        API endpoint to delete a menu.

        Methods:
            delete(): Handle DELETE requests for a menu.

        Usage:
            Send a delete request to '/vendor-api/menu/<int:menu_id>' with logged-in user

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        menu = self.db.query(Menu).filter_by(id=menu_id)
        if not menu.first():
            return forbidden_error(msg="Menu doesn't exists")

        try:
            menu.delete()
            self.db.commit()
            return success_response(msg='Menu deleted successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot delete menu')
        finally:
            self.db.close()


class FoodItemListApi(DobatoApi):
    def post(self):
        """
        API endpoint to add new food-item.

        Methods:
            post(): Handle POST requests for food-item.

        Usage:
            Send a post request to '/vendor-api/food-items' with logged-in user and data
            containing 'item_name', 'item_description', 'item_price', 'type'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        if not user:
            return bad_request_error(msg="User doesn't exists")

        data = request.get_json()
        food_item_schema = FoodItemSchema()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()

        if not vendor_profile:
            return bad_request_error(msg="Vendor Profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        # try:
        #     item_price = float(data.get('item_price'))
        #     data['item_price'] = item_price
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are numbers.')

        try:
            validated_data = food_item_schema.load(data)
            validated_data['vendor_profile_id'] = vendor_profile.id
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            new_data = FoodItem(**validated_data)
            self.db.add(new_data)
            self.db.commit()
            return success_response(msg='Food item added successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot add new food item')
        finally:
            self.db.close()

    def get(self):
        """
        API endpoint to get vendor food-items.

        Methods:
            get(): Handle get requests for a vendor food-items.

        Usage:
            Send a get request to '/vendor-api/food-items' with logged-in user.

        Returns:
            JSON response with vendor food-items.
        """
        user = load_current_user()
        food_item_data = (self.db.query(FoodItem)
                          .join(VendorProfile, VendorProfile.id == FoodItem.vendor_profile_id)
                          .filter(VendorProfile.user_id == user.id)
                          .filter(VendorProfile.id == FoodItem.vendor_profile_id)).all()

        if food_item_data:
            return self.list_response(food_item_data)
        else:
            return not_found_error(msg="No food item data for this vendor")


class FoodItemDetailApi(DobatoApi):
    def get(self, item_id):
        """
        API endpoint to get food-item detail.

        Methods:
            get(): Handle get requests for a food-item detail.

        Usage:
            Send a get request to '/vendor-api/food-items/<int:item_id>' with logged-in user.

        Returns:
            JSON response with venue data.
        """
        user = load_current_user()
        #TODO : need to check if user exists, plus if user is verified and vendor, i.e. check if current user is customer or vendor as well(recreate by sending empty bearer token)
        food_item_detail = (self.db.query(FoodItem)
                            .join(VendorProfile, VendorProfile.id == FoodItem.vendor_profile_id)
                            .filter(VendorProfile.user_id == user.id)
                            .filter(FoodItem.id == item_id))
        data = food_item_detail.first()
        if data:
            return self.detail_response(data)
        else:
            return not_found_error(msg="No data for this food-item")

    def put(self, item_id):
        """
        API endpoint to update a food-item.

        Methods:
            put(): Handle PUT requests for a food-item.

        Usage:
            Send a put request to '/vendor-api/food-items/<int:item_id>' with logged-in user
            and food-item data containing 'item_name', 'item_description', 'item_price', 'type'

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()

        if not vendor_profile:
            return bad_request_error(msg="Vendor Profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        food_item = (self.db.query(FoodItem)
                     .join(VendorProfile, VendorProfile.id == FoodItem.vendor_profile_id)
                     .filter(VendorProfile.user_id == user.id)
                     .filter(Menu.id == item_id)).first()
        if not food_item:
            return forbidden_error(msg="Food item doesn't exists")

        data = request.get_json()
        food_item_schema = FoodItemSchema()
        # try:
        #     item_price = float(data.get('item_price'))
        #     data['item_price'] = item_price
        # except ValueError:
        #     return bad_request_error(msg='Invalid input. Please ensure numbers are integers.')

        try:
            validated_data = food_item_schema.load(data)
            validated_data['vendor_profile_id'] = food_item.vendor_profile_id
        except validate.ValidationError as err:
            return validation_error(err)
        try:
            for key, value in validated_data.items():
                setattr(food_item, key, value)
            self.db.commit()
            return success_response(msg='Food itme updated successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot update food item')
        finally:
            self.db.close()

    def delete(self, item_id):
        """
        API endpoint to delete a food-item.

        Methods:
            delete(): Handle DELETE requests for a food-item.

        Usage:
            Send a delete request to '/vendor-api/food-items/<int:item_id>' with logged-in user

        Returns:
            JSON response with success message.
        """
        user = load_current_user()
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        food_item = self.db.query(FoodItem).filter_by(id=item_id)
        if not food_item.first():
            return forbidden_error(msg="Food item doesn't exists")

        try:
            food_item.delete()
            self.db.commit()
            return success_response(msg='Food item deleted successfully')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot delete food item')
        finally:
            self.db.close()


class MenuFoodItemApi(DobatoApi):
    # TODO: few steps needed for completion and error handling, check user missing as well?
    def get(self, menu_id):
        """
        API endpoint to get menu food-items.

        Methods:
            get(): Handle get requests for a menu food-items.

        Usage:
            Send a get request to '/vendor-api/menu/<int:menu_id>/menu-items' with logged-in user.

        Returns:
            JSON response with menu food-items.
        """
        menu = self.db.query(Menu).filter_by(id=menu_id).first()
        if not menu:
            return bad_request_error("Menu doesn't exists")

        query = (self.db.query(MenuItemTable)
                 .join(Menu, Menu.id == MenuItemTable.menu_id)
                 .join(FoodItem, FoodItem.id == MenuItemTable.item_id)
                 .filter(MenuItemTable.menu_id == menu_id)
                 .with_entities(Menu.name.label('menu_name'), FoodItem.item_name.label('item_name')))
        rows = query.all()
        return self.list_response(rows)

    def post(self, menu_id):
        """
        API endpoint to add new food-item in menu.

        Methods:
            post(): Handle POST requests for food-item in menu.

        Usage:
            Send a post request to '/vendor-api/menu/<int:menu_id>/menu-items' with logged-in user and data
            like {'menu_items': [{'item_id':0, 'menu_id':menu_id}]}

        Returns:
            JSON response with success message.
        """
        user = self.user
        #TODO : need to check if user exists, plus if user is verified and vendor, i.e. check if current user is customer or vendor as well(recreate by sending empty bearer token)
        vendor_profile = self.db.query(VendorProfile).filter_by(user_id=user.id).first()
        if not vendor_profile:
            return bad_request_error("Vendor profile doesn't exists")

        if not self.is_vendor_verified(vendor_profile):
            return unauthorized_response(msg="Vendor is not verified yet.")

        menu_exists = self.db.query(Menu).filter_by(id=menu_id).first()
        if not menu_exists:
            return bad_request_error("Menu doesn't exists")

        data = request.get_json()
        menu_items = data.get('menu_items')
        for item_data in menu_items:
            item_data['menu_id'] = menu_id
            try:
                new_data = MenuItemTable(**item_data)
                self.db.add(new_data)
                self.db.commit()
            except SQLAlchemyError as e:
                self.db.rollback()
                return server_error(msg='Cannot add new food item')
            finally:
                self.db.close()
        return success_response(msg='Food item added successfully')


class MenuFoodItemDetailApi(DobatoApi):
    def delete(self, menu_id, menu_food_item_id):
        """
        API endpoint to delete a menu food-item.

        Methods:
            delete(): Handle DELETE requests for a menu food-item.

        Usage:
            Send a delete request to '/vendor-api/menu/<int:menu_id>/menu-items/<int:menu_food_item_id>'
            with logged-in user

        Returns:
            JSON response with success message.
        """

        menu = self.db.query(Menu).filter_by(id=menu_id).first()
        if not menu:
            return bad_request_error("Menu doesn't exists")

        food_item = self.db.query(MenuItemTable).filter_by(id=menu_food_item_id)
        if not food_item.first():
            return forbidden_error(msg="Menu Food item doesn't exists")

        try:
            food_item.delete()
            self.db.commit()
            return success_response(msg='Food item deleted successfully from menu')
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg='Cannot delete food item from menu')
        finally:
            self.db.close()


class VendorIndustryList(DobatoApi):
    """
    Class representing the API endpoint for vendor industry list.

    Inherits:
        DobatoApi: Base class for Dobato API endpoints.

    Methods:
        get(): Handle GET requests for vendor industry list.

    Usage:
        Send a GET request to '/vendor-api/vendor-industry-list'

    """

    def get(self):
        """
        Handle GET requests for vendor industry list.

        Returns:
            JSON response with vendor-industry data and success message.
        """
        # get list of vendor industries eg: venues, photography etc.
        # TODO: try-catch here
        rows = self.db.query(VendorIndustry.id, VendorIndustry.industry_name).all()
        return self.list_response(rows)