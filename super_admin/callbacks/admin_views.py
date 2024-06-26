import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from super_admin.utils.admin_site import admin_assets
from utilities.vendor_forms import VendorForms
from vendor_app.callbacks.user_validators import VendorIndustrySchema, UserTypeSchema
from vendor_app.utils.dynamic_fields import VENDOR_INDUSTRY_ADDITIONAL_FIELDS
from utilities.dobato import DobatoApi
from utilities.responses import *
from flask import request, jsonify, current_app

from utilities.schemas.models import VendorIndustry, UserType, User


class GetFormType(DobatoApi):
    def get(self):
        form_factory = VendorForms()
        return jsonify({'form_types': form_factory.get_forms()})



class AddVendorForm(DobatoApi):
    def get(self):
        return jsonify(VENDOR_INDUSTRY_ADDITIONAL_FIELDS)

    def post(self):
        data = request.get_json()
        vendor_id = data['vendor_id']
        form_type = data


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


class ListRegisteredTables(DobatoApi):
    def get(self):
        db_tables = admin_assets.get_table_list()
        table_list = []
        for table_name, model in db_tables.items():
            table_list.append({table_name: model.__name__})
        return jsonify({'data': table_list, 'status': 200})


class ListTableData(DobatoApi):
    def get(self, table_name):
        sql_model = admin_assets.get_model_from_table(table_name)
        exposed_columns = admin_assets.exposed_attrs.get(table_name)
        rows = self.db.query(sql_model).all()
        results = list()
        if rows:
            for row in rows:
                result = dict()
                if exposed_columns:
                    object_name = ' '.join([str(getattr(row, col.name)) for col in exposed_columns])
                else:
                    object_name = f"Object {row.id}"
                result[row.id] = object_name
                results.append(result)
        return self.list_response({'data': results})


class AddItem(DobatoApi):
    def post(self, table_name):
        data = request.form
        sql_model = admin_assets.get_model_from_table(table_name)
        try:
            sql_object = sql_model(**data)
            self.db.add(sql_object)
            self.db.commit()
        except SQLAlchemyError:
            raise Exception(f"unable to create data for table {table_name}")


class ItemDetail(DobatoApi):
    def get(self, table_name, item_id):
        sql_model = admin_assets.get_model_from_table(table_name)
        datatype_details = dict()
        columns = inspect(sql_model).columns
        for column in columns:
            datatype_details[column.name] = str(column.type)
        if not sql_model:
            return not_found_error(msg="table not found or its not registered table. "
                                       "please register table in admin_site.py")
        item = self.db.query(sql_model).filter(sql_model.id == item_id).first()
        if item:
            result = self.make_obj_serializable(item)
            related_data = {}
            for relationship in inspect(sql_model).relationships:
                related_table_name = relationship.mapper.class_.__name__
                related_rows = self.db.query(relationship.mapper.class_).all()
                related_data[related_table_name] = self.make_obj_serializable(related_rows)
            return jsonify({'data': result, 'meta': {'foreign_keys': related_data,
                                                     'data_type_details': datatype_details}})
        return not_found_error(msg="item doesn't exist in the database")

    def put(self, table_name, item_id):
        sql_model = admin_assets.get_model_from_table(table_name)
        item = self.db.query(sql_model).filter(sql_model.id == item_id).first()
        if not item:
            return not_found_error(msg="item doesn't exist in the database")
        data = request.json
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        return success_response(msg=f"{table_name} item updated successfully")

    def delete(self, table_name, item_id):
        sql_model = admin_assets.get_model_from_table(table_name)
        item = self.db.query(sql_model).filter(sql_model.id == item_id).first()
        if not item:
            return not_found_error(msg="item doesn't exist in the database")
        try:
            self.db.delete(item)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            return server_error(msg=f"unable to delete item. "
                                    f"Error details:{str(e)}")
        return success_response(msg="item deleted successfully")
