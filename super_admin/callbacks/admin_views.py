import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from super_admin.utils.admin_site import admin_assets

from utilities.dobato import DobatoApi
from utilities.responses import *
from flask import request, jsonify, current_app

from utilities.schemas.models import VendorIndustry, UserType, User


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


class VendorIndustryList(DobatoApi):
    """
    Class representing the API endpoint for vendor industry list.

    Inherits:
        DobatoApi: Base class for Dobato API endpoints.

    Methods:
        get(): Handle GET requests for vendor industry list.

    Usage:
        Send a GET request to '/admin-api/vendor-industry-list'

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