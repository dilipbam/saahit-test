from flask import request

from utilities.dobato import DobatoApi
from utilities.responses import bad_request_error, success_response
from utilities.schemas.models import VendorProfile


class VendorShiftApi(DobatoApi):
    def post(self, vendor_profile_id):
        # Incomplete API
        data = request.get_json()
        vendor_profile = self.db.query(VendorProfile).filter_by(id=vendor_profile_id).first()
        if not vendor_profile:
            return bad_request_error("Vendor Profile doesn't exists.")

        return success_response("Shift added for vendor")