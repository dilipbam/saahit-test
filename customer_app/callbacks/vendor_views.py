
from flask import request
from sqlalchemy import func

from utilities.db_getter import get_session
from utilities.dobato import DobatoApi
from utilities.responses import success_response, not_found_error
from utilities.schemas.models import VendorIndustry, VenueType, Venue, VendorProfile, VenueBooking, VenueSpace, Menu, \
    MenuItemTable, FoodItem


class VendorIndustryList(DobatoApi):
    """
    Class representing the API endpoint for vendor industry list.

    Inherits:
        DobatoApi: Base class for Dobato API endpoints.

    Methods:
        get(): Handle GET requests for vendor industry list.

    Usage:
        Send a GET request to '/consumer-api/vendor-industry-list'

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


class VenueTypeList(DobatoApi):
    def get(self):
        """
        API endpoint for vendor industry list.

        Methods:
            get(): Handle GET requests for vendor industry list.

        Usage:
            Send a GET request to '/consumer-api/vendor-industry-list'

        Returns:
            JSON response with vendor-industry data and success message.
        """
        # get list of venue types eg: banquet, resort, five star etc.
        venue_types = self.db.query(VenueType).all()
        return self.list_response(rows=venue_types)


class VenueList(DobatoApi):
    def get(self):
        """
        API endpoint for venues list.

        Methods:
            get(): Handle GET requests for venues list.

         Usage:
            Send a GET request to '/consumer-api/venues-list'

        Returns:
            JSON response with venue-list data and success message.
        """
        venue_query = (self.db.query(Venue)
                       .join(VenueSpace, Venue.id == VenueSpace.venue_id)
                       .join(VendorIndustry, Venue.industry_id == VendorIndustry.id)
                       .group_by(Venue.id, VendorIndustry.industry_name)
                       .with_entities(Venue.id.label('venue_id'), Venue.location, Venue.venue_type, Venue.venue_name,
                                      VendorIndustry.industry_name, Venue.parking_capacity, Venue.vendor_profile_id,
                                      func.sum(VenueSpace.seating_capacity + VenueSpace.floating_capacity).label('total_capacity')))
        # venue_query = (self.db.query(VendorProfile)
        #                .join(VendorIndustry, VendorProfile.industry_id == VendorIndustry.id)
        #                .join(Venue, VendorProfile.industry_id == Venue.industry_id)
        #                # .filter(VendorIndustry.industry_name == 'Venues')
        #                .with_entities(VendorProfile.id, Venue.venue_name, VendorIndustry.industry_name,
        #                               VendorProfile.profile_image, VendorProfile.location))
        #
        location_filter = request.args.get('location')
        if location_filter:
            venue_query = venue_query.filter(VendorProfile.location == location_filter)

        # TODO: implement date filter
        date_filter = request.args.get('date')

        venues_list = venue_query.limit(self.limit()).offset(self.offset()).all()
        # venues_count = venue_query.scalar()
        # pagination_meta = self.pagination_meta(venues_count)
        return self.list_response(rows=venues_list)


class VenueDetail(DobatoApi):
    def get(self, vendor_profile_id):
        """
        API endpoint for venue detail.

        Methods:
            get(): Handle GET requests for venue detail.

        Usage:
            Send a GET request to '/consumer-api/venue-detail/<int:vendor_profile_id>'

        Returns:
            JSON response with detail data about venue and its related spaces.
        """
        venue_detail_query = (self.db.query(VendorProfile)
                              .join(Venue, Venue.vendor_profile_id == VendorProfile.id)
                              .join(VenueSpace, Venue.id == VenueSpace.venue_id)
                              .filter(VendorProfile.id == vendor_profile_id)
                              .group_by(Venue.id)
                              .with_entities(Venue.vendor_profile_id, Venue.id.label('venue_id'), Venue.venue_name,
                                             Venue.venue_type, Venue.location,
                                             func.json_agg(func.json_build_object(
                                                 'space_id', VenueSpace.id,
                                                 'space_name', VenueSpace.space_name,
                                                 'seating_capacity', VenueSpace.seating_capacity,
                                                 'floating_capacity', VenueSpace.floating_capacity,
                                                 'space_type', VenueSpace.floating_capacity
                                             )).label('Space_info')))

        venue_detail = venue_detail_query.all()
        if venue_detail:
            return self.detail_response(venue_detail[0])
        else:
            return not_found_error(msg="Venue detail not found")


class VendorMenuList(DobatoApi):
    def get(self, vendor_profile_id):
        """
        API endpoint for vendor menu list.

        Methods:
            get(): Handle GET requests for vendor menu list.

        Usage:
            Send a GET request to '/consumer-api/menu-list/<int:vendor_profile_id>'

        Returns:
            JSON response with list of menus for a vendor.
        """
        vendor_menu_query = self.db.query(Menu).filter(Menu.vendor_profile_id == vendor_profile_id)
        vendor_menu = vendor_menu_query.limit(self.limit()).offset(self.offset()).all()

        return self.list_response(vendor_menu)


class VendorMenuDetail(DobatoApi):
    def get(self, menu_id):
        """
        API endpoint for menu food items list.

        Methods:
            get(): Handle GET requests for menu food items list.

        Usage:
            Send a GET request to '/consumer-api/menu-list/<int:vendor_profile_id>/food-items/<int:menu_id>'

        Returns:
            JSON response with list of food-items of a menu.
        """
        menu_detail_query = (self.db.query(MenuItemTable)
                             .join(FoodItem, FoodItem.id == MenuItemTable.item_id)
                             .filter(MenuItemTable.menu_id == menu_id)
                             .with_entities(MenuItemTable.id, MenuItemTable.menu_id, FoodItem.item_name, FoodItem.type,
                                            FoodItem.item_price))

        menu_items_list = menu_detail_query.limit(self.limit()).offset(self.offset()).all()
        return self.list_response(menu_items_list)


class VendorCalendar(DobatoApi):
    def get(self, **kwargs):
        # IN-COMPLETE
        vendor_id = kwargs['vendor_id']
        date_from = kwargs['date_from']
        date_to = kwargs['date_to']
        venue_bookings = (self.db.query(VenueBooking)
                          .filter(VenueBooking.booked_date >= date_from)
                          .filter(VenueBooking.booked_date <= date_to)
                          .with_entities(VenueBooking.booked_date).all())

        return venue_bookings