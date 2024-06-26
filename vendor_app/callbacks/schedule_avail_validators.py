import re
from datetime import datetime

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


def convert_time_string_to_time_object(time_string):
    return datetime.strptime(time_string, '%I:%M %p').time()


class ShiftSchema(Schema):
    """
    Attributes:
        shift_time (str): Time of the shift in 12-hour format (e.g. 10:30 AM)
        booking_capacity (int): Booking capacity for the shift (default=1)
    """
    id = fields.Int(dump_only=True)
    shift_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    shift_time = fields.Time(required=True,
                             validate=validate.Regexp(re.compile(r'^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] (AM|PM)$')))
    booking_capacity = fields.Int(required=True, validate=validate.Range(min=1))
    vendor_profile_id = fields.Int(required=True, validate=validate.Range(min=1))
    space_id = fields.Int(required=False)

    def _deserialize(self, value, attr, data, **kwargs):
        time_object = super()._deserialize(value, attr, data, **kwargs)
        return convert_time_string_to_time_object(time_object)


class ScheduleSchema(Schema):
    """
    Schedule schema
    schedule (dict): Schedule data in JSON format
    """
    id = fields.Int(dump_only=True)
    schedule = fields.Raw(required=True)
    vendor_profile_id = fields.Int(required=True, validate=validate.Range(min=1))
    space_id = fields.Int()


class AvailabilitySchema(Schema):
    """
    Availability schema
    Attributes:
        date (date): Date of the availability
        status (str): Status of the availability (one of "available", "unavailable", "pending")
    """
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["available", "unavailable", "pending"]))
    shift_id = fields.Int(required=True, validate=validate.Range(min=1))
    vendor_profile_id = fields.Int(required=True, validate=validate.Range(min=1))
    space_id = fields.Int()
