from marshmallow import fields


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

required_field_error = {'invalid': 'Invalid', 'required': 'Required'}
invalid_field_error = {'invalid': 'Invalid Phone Number'}
