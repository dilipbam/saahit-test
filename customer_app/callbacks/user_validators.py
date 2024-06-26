from marshmallow import Schema, fields, ValidationError, validate

from customer_app.utils.custom_errors import required_field_error, invalid_field_error


class CleanedString(fields.String):
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
        if not field and self.required:
            raise self.make_error("required")
        super(CleanedString, self)._validate(field)


class StringNumberField(fields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)


class LoginSchema(Schema):
    email = fields.String(required=True, error_messages=required_field_error)
    password = fields.String(required=True, error_messages=required_field_error)


class RegisterSchema(Schema):
    fullname = CleanedString(required=True, error_messages=required_field_error)
    password = fields.String(required=True, error_messages=required_field_error)
    confirm_password = fields.String(required=True, error_messages=required_field_error)
    email = CleanedString(required=True, error_messages=required_field_error)
    phone_number = StringNumberField(required=True,
                                     validate=validate.Regexp(regex=r'^\d{10}$', flags=0),
                                     error_messages=invalid_field_error)  # TODO:empty value validation somehwere before this step


class UserProfileSchema(Schema):
    """
        A Marshmallow schema for user profile data validation.

        Attributes:
            firstname (fields.String, required=True): The user's firstname.
            lastname (fields.String, required=True): The user's lastname.
            email (fields.String, required=True): The user's email address.
            phone_number (fields.String, required=True): The user's phone number.
            image (fields.String, required=False): The user's profile image.

        Methods:
            load(data, *, partial=False, unknown=None, session=None) -> dict:
                Deserialize the given data into a user profile object.

            dump(data, *, partial=False, many=False) -> dict:
                Serialize the given user profile object into a dictionary.
        """
    first_name = CleanedString(required=True)
    last_name = CleanedString(required=True)
    email = fields.Email(required=True)
    phone_number = fields.Integer(required=True,
                                  validate=validate.Regexp(regex=r'^\d{10,15}$', error='Invalid phone number'))
    image_extension = CleanedString(required=False)

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
