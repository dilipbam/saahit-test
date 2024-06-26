
from utilities.db_getter import get_session
from utilities.schemas.models import Venue, VendorIndustry, VendorProfile

# Create a Session
session = get_session()

# Add sample data
# vendor_industry = VendorIndustry(industry_name="Event Planning", additional_fields={"key": "value"})
# session.add(vendor_industry)
# session.flush()
# vendor_profile = VendorProfile(
#     user_id=3,
#     vendor_type="Catering",
#     industry_id=vendor_industry.id,
#     estd_date='2020-01-01',
#     location="456 Main St",
#     profile_image="profile.jpg",
#     pan_number="ABCDE1234F",
#     pan_image="pan_image.jpg",
#     pan_holder_citizenship="citizenship.jpg",
#     pan_holder_photo="holder_photo.jpg",
#     last_updated='2024-01-01',
#     is_sa_verified=True
# )
#
# session.add(vendor_profile)
# session.commit()
# print("profile",vendor_profile.id)
# Assuming vendor_profile table exists and contains a record with id=1
venue = Venue(
    venue_name="Grand Hall",
    location="123 Main St",
    mandatory_catering=True,
    venue_type="Conference Center",
    parking_capacity=100,
    industry_id=12,
    vendor_profile_id=10  # This should be an existing vendor_profile ID
)

session.add(venue)

# Add and commit the changes
session.commit()

# Close the session
session.close()