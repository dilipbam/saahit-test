from utilities.schemas.models import User, VendorIndustry, UserType, Venue


class AdminSite(object):
    def __init__(self):
        self.models = dict()
        self.exposed_attrs = dict()

    def register(self, model, exposed_attrs=None):
        self.models[model.__tablename__] = model
        if exposed_attrs:
            self.exposed_attrs[model.__tablename__] = exposed_attrs

    def get_model(self, table_name):
        return self.models[table_name]

    def get_table_list(self):
        return self.models

    def get_model_from_table(self, table_name):
        model = self.models.get(table_name)
        return model


admin_assets = AdminSite()
admin_assets.register(User, exposed_attrs=[User.email,User.user_type_id, User.created_at])
admin_assets.register(VendorIndustry)
admin_assets.register(UserType)
admin_assets.register(Venue)
