from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from super_admin.validators.schema_validators import VendorFormSchema
from utilities.dobato import DobatoApi
from utilities.responses import success_response
from utilities.schemas.models import VendorIndustry, VendorDynamicFormTable
from utilities.vendor_forms import VendorForms
from vendor_app.callbacks.validators.user_validators import VendorIndustrySchema
from vendor_app.utils.dynamic_fields import VENDOR_INDUSTRY_ADDITIONAL_FIELDS


class GetFormType(DobatoApi):
    def get(self):
        form_factory = VendorForms()
        return jsonify({'form_types': form_factory.get_forms()})


class AddVendorForm(DobatoApi):
    def get(self):
        return jsonify(VENDOR_INDUSTRY_ADDITIONAL_FIELDS)

    def post(self):
        data = request.get_json()
        try:
            validated_data = VendorFormSchema().load(data)
        except ValidationError as err:
            raise err

        form_obj = VendorDynamicFormTable(**validated_data)
        try:
            self.db.add(form_obj)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
        return success_response(msg="Form added successfully")





# saahitt admin to add industries for vendors
class AddVendorIndustry(DobatoApi):
    """
        Class takes industry name to be added by business/operations team at Saahitt
    """

    def get(self):
        vendor_industry_fields = VENDOR_INDUSTRY_ADDITIONAL_FIELDS
        return jsonify(vendor_industry_fields)

    def post(self):
        # get database session
        vendor_industry_data = request.json
        vendor_industry_schema = VendorIndustrySchema()

        try:
            validated_industry_data = vendor_industry_schema.load(vendor_industry_data)
        except Exception as e:
            raise e

        vendor_industry_name = validated_industry_data['industry_name']
        try:
            vendor_industry = self.db.query(VendorIndustry).filter_by(industry_name=vendor_industry_name).first()
        except SQLAlchemyError as e:
            vendor_industry = None
        if vendor_industry:
            return jsonify({'message': 'Vendor Industry already exists'})
        try:
            new_industry = VendorIndustry(**validated_industry_data)
            self.db.add(new_industry)
            self.db.commit()
            return success_response('Vendor Industry added successfully')
        except Exception as e:
            self.db.rollback()
            return jsonify({'message': str(e)})
        finally:
            self.db.close()
