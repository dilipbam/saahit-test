from marshmallow import Schema, fields

from super_admin.utils.validator_utlils import CleanedString


class UserSchema:
    pass


class VendorFormSchema(Schema):
    form_type = CleanedString(required=True)
    schema = fields.String()
    vendor_type = CleanedString(required=True)


