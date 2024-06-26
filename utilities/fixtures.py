from utilities.dobato import DobatoApi
from utilities.schemas.models import UserType, VendorIndustry
from flask import Flask

# Initialize Flask application
app = Flask(__name__)

class Fixtures(DobatoApi):
    def insert_data(self):
        """Insert initial data into the database."""
        try:
            # Check if UserType records exist, add them if they don't
            if not self.db.query(UserType).filter_by(type_name="SuperAdmin").first():
                self.db.add(UserType(type_name="SuperAdmin"))
                print("Inserted: SuperAdmin")
            else:
                print("SuperAdmin already exists.")

            if not self.db.query(UserType).filter_by(type_name="Consumer").first():
                self.db.add(UserType(type_name="Consumer"))
                print("Inserted: Consumer")
            else:
                print("Consumer already exists.")

            if not self.db.query(UserType).filter_by(type_name="Vendor").first():
                self.db.add(UserType(type_name="Vendor"))
                print("Inserted: Vendor")
            else:
                print("Vendor already exists.")

            # Check if VendorIndustry records exist, add them if they don't (INDUSTRY TABLE)
            if not self.db.query(VendorIndustry).filter_by(industry_name="Venues").first():
                self.db.add(VendorIndustry(industry_name="Venues"))
                print("Inserted: Venues")
            else:
                print("Venues already exists.")

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error inserting data: {e}")
        finally:
            self.db.close()


if __name__ == "__main__":
    with app.app_context():
        fixture_instance = Fixtures()
        fixture_instance.insert_data()
