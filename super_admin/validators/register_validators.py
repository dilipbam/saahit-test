from super_admin.validators.schema_validators import UserSchema
from utilities.schemas.models import User

validator_map = {User.__tablename__: UserSchema}
