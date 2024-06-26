from marshmallow import Schema, fields, ValidationError, validate, validates

from vendor_app.utils.custom_errors import required_field_error


class CleanedString(fields.String):
    """
    A custom Marshmallow string field that cleans the input string by removing leading and trailing whitespaces.

    Args:
        clean (bool, optional): If True, the input string will be cleaned by removing leading and trailing whitespaces.
                                Defaults to True.
        *args, **kwargs: Additional arguments and keyword arguments to be passed to the parent class.

    Attributes:
        clean (bool): A flag indicating whether the input string should be cleaned or not.

    Methods:
        _cleaned_string(field) -> str:
            Clean the given field by removing leading and trailing whitespaces if the clean flag is set to True.

        _deserialize(field, attr, obj, **kwargs) -> str:
            Deserialize the given field and apply the cleaning process if the clean flag is set to True.

        _validate(field) -> None:
            Validate the given field and raise a validation error if the field is missing and the field is required.
    """

    def __init__(self, clean=True, *args, **kwargs):
        self.clean = clean
        super(CleanedString, self).__init__(*args, **kwargs)

    def _cleaned_string(self, field):
        if not field or not self.clean:
            return field
        return field.strip()

    def _deserialize(self, field, attr, obj, **kwargs):
        field = super(CleanedString, self)._deserialize(field, attr, obj, **kwargs)
        return self._cleaned_string(field)

    def _validate(self, field):
        if not field or self.required:
            raise self.make_error('required')
        super(CleanedString, self)._validate(field)


class StringNumberField(fields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)


# SCHEMAS START
class LoginSchema(Schema):
    """
    A Marshmallow schema for user login data.
    Attributes:
        email (CleanedString, required=True): The user's email.
        password (fields.String, required=True): The user's password.

    Methods:
        load(data, *, partial=False, unknown=None, session=None) -> dict:
            Deserialize the given data into a user login object.

        dump(data, *, partial=False, many=False) -> dict:
            Serialize the given user login object into a dictionary.
    """
    email = fields.String(required=True, error_messages=required_field_error)
    password = fields.String(required=True, error_messages=required_field_error)


class RegisterSchema(Schema):
    """
    A Marshmallow schema for user registration data.

    Attributes:
        fullname (fields.String, required=True): The user's fullname.
        password (fields.String, required=True): The user's password.
        email (fields.String, required=True): The user's email address.
        phone_number (fields.String, required=True): The user's phone number.

    Methods:
        load(data, *, partial=False, unknown=None, session=None) -> dict:
            Deserialize the given data into a user registration object.

        dump(data, *, partial=False, many=False) -> dict:
            Serialize the given user registration object into a dictionary.
    """
    fullname = fields.String(required=True, error_messages=required_field_error)
    password = fields.String(required=True, error_messages=required_field_error)
    confirm_password = fields.String(required=True, error_messages=required_field_error)
    email = fields.String(required=True, error_messages=required_field_error)
    phone_number = StringNumberField(required=True,
                                     validate=validate.Regexp(regex=r'^\d{10}$', flags=0, error='invalid'),
                                     error_messages=required_field_error)  # TODO:empty value validation somehwere before this step


class VendorProfileSchema(Schema):
    """
        A Marshmallow schema for vendor profile data validation.

        Attributes:
            business name (fields.String, required=True): The vendor's business name.
            email (fields.String, required=True): The user's email address.
            phone_number (fields.String, required=True): The user's phone number.
            profileimage (fields.String, required=False): The user's profile image.


        Methods:
            load(data, *, partial=False, unknown=None, session=None) -> dict:
                Deserialize the given data into a user profile object.

            dump(data, *, partial=False, many=False) -> dict:
                Serialize the given user profile object into a dictionary.
        """
    vendor_type = fields.String(required=True)
    industry_id = fields.String(required=True)
    profile_image = fields.Field(required=False)
    estd_date = fields.Date(required=False)
    location = fields.String(required=True)
    # base_price = fields.String(required=False)
    pan_number = fields.String(required=True, validate=validate.Regexp(regex=r'^\d*$',
                                                                       error='Invalid VAT/PAN Registration Number'))
    pan_image = fields.Field(required=True)
    pan_holder_citizenship = fields.Field(required=True)
    pan_holder_photo = fields.Field(required=True)

    # Custom validation methods for profile
    def validate_image_extension(self, value):
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Add more extensions if needed
        if value.lower() not in allowed_extensions:
            raise ValidationError(f'Unsupported image format: {value}')

    def validate(self, data, **kwargs):
        errors = {}
        # Custom validations
        if 'image' not in data or not data['image']:
            errors['image'] = ['Image is required']

        if errors:
            raise ValidationError(errors)

        return data


class VenueSchema(Schema):
    venue_name = fields.String(required=True)
    location = fields.Str(required=True)
    mandatory_catering = fields.Boolean(required=True)
    venue_type = fields.String(required=True)
    parking_capacity = fields.Integer(required=False)
    industry_id = fields.Integer(required=True)


# TODO: used for all file/image validations should work???? but didn't??? GET BACK LATER
class FileSchema(Schema):
    #     image = fields.Raw(
    #         validate=[
    #             validate(
    #                 max_size=5 * 1024 * 1024,  # Limit file size to 5 MB
    #                 extensions=['jpg', 'jpeg', 'png', 'gif'],
    #                 error='Invalid file extension or size'
    #             )
    #         ]
    #     )

    @validates('image')
    def validate_image_extension(self, value):
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Add more extensions if needed
        if value.filename and value.filename.lower().endswith(tuple(allowed_extensions)) is False:
            raise ValidationError(f'Unsupported image format: {value.filename}')

    @validates('image')
    def validate_image_size(self, value):
        max_size = 5 * 1024 * 1024  # Limit file size to 5 MB
        if value.filename and value.size > max_size:
            raise ValidationError(f'File size exceeds the limit: {value.filename}')


# TODO: needs rechecking my mind is boggled
class SpacesSchema(Schema):
    space_name = fields.String(required=True)
    space_type = fields.String(required=True)
    description = fields.String(required=True)
    type_of_charge = fields.String(required=True)
    rate = fields.Integer(required=True)
    seating_capacity = fields.Integer(required=True)
    floating_capacity = fields.Integer(required=True)

    def validate_image_extension(value):
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Add more extensions if needed
        if str(value).lower() not in allowed_extensions:
            raise ValidationError(f'Unsupported image format: {value}')


class AdditionalFieldSchema(Schema):
    field_name = fields.String(required=True)
    display_name = fields.String(required=True)
    type_of_field = fields.String(required=True)
    data_type=fields.String(required=True)

    # Add more fields as needed


class VendorIndustrySchema(Schema):
    industry_name = fields.String(required=True)
    additional_fields = fields.List(fields.Nested(AdditionalFieldSchema), required=False)


class UserTypeSchema(Schema):
    type_name = fields.String(required=True)


class MenuSchema(Schema):
    name = fields.String(required=True)
    no_of_items = fields.Integer(required=True)
    cuisine = CleanedString(required=False)
    rate = fields.Float(required=True)
    description = CleanedString(required=False)
    vendor_profile_id = fields.Integer(required=True)


class FoodItemSchema(Schema):
    item_name = fields.String(required=True)
    item_description = CleanedString(required=False)
    type = CleanedString(required=False)
    item_price = fields.Float(required=True)


class MenuItemSchema(Schema):
    menu_id = fields.Int(required=True)
    item_id = fields.Int(required=True)

    @validates('menu_id')
    def validate_menu_id(self, value):
        if value <= 0:
            raise ValidationError('menu_id must be a positive integer')

    @validates('item_id')
    def validate_item_id(self, value):
        if value <= 0:
            raise ValidationError('item_id must be a positive integer')

