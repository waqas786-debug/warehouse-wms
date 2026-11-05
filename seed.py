from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.auth import Role, User, StaffProfile
from app.models.facility import Warehouse, Zone, Aisle, Rack, Shelf, StorageBin
from app.models.catalog import ProductCategory, UnitOfMeasure, Product
from app.models.inventory import BinStock

app = create_app()

with app.app_context():
    print("Initializing database and creating all 42 tables...")
    db.create_all()

    table_count = len(db.metadata.tables.keys())
    print(f"Total Registered Tables: {table_count}")

    if not Role.query.first():
        # Roles & Admin User
        admin_role = Role(name='Administrator', description='Full system access')
        db.session.add(admin_role)
        db.session.flush()

        admin_user = User(
            role_id=admin_role.id,
            username='admin',
            email='admin@wms.local',
            password_hash=generate_password_hash('admin123'),
            is_active=True
        )
        db.session.add(admin_user)
        db.session.flush()

        profile = StaffProfile(
            user_id=admin_user.id,
            first_name='System',
            last_name='Admin',
            shift_type='Morning'
        )
        db.session.add(profile)

        # Facility Setup
        wh = Warehouse(name='Central Distribution Hub', code='WH-LHE-01', city='Lahore', total_capacity_sqft=50000.0)
        db.session.add(wh)
        db.session.flush()

        zone = Zone(warehouse_id=wh.id, name='Zone A - Fast Moving', zone_type='Dry')
        db.session.add(zone)
        db.session.flush()

        aisle = Aisle(zone_id=zone.id, aisle_code='A01')
        db.session.add(aisle)
        db.session.flush()

        rack = Rack(aisle_id=aisle.id, rack_code='R01')
        db.session.add(rack)
        db.session.flush()

        shelf = Shelf(rack_id=rack.id, level_number=1)
        db.session.add(shelf)
        db.session.flush()

        bin1 = StorageBin(shelf_id=shelf.id, bin_barcode='BIN-A01-R01-S01-01')
        bin2 = StorageBin(shelf_id=shelf.id, bin_barcode='BIN-A01-R01-S01-02')
        db.session.add_all([bin1, bin2])
        db.session.flush()

        # Catalog Setup
        cat = ProductCategory(name='Electronics', slug='electronics')
        uom = UnitOfMeasure(unit_name='Piece', abbreviation='PCS')
        db.session.add_all([cat, uom])
        db.session.flush()

        p1 = Product(category_id=cat.id, uom_id=uom.id, sku='SKU-BARCODE-RDR', barcode='890123456789', name='Industrial Barcode Scanner', reorder_threshold=5)
        p2 = Product(category_id=cat.id, uom_id=uom.id, sku='SKU-THERM-LBL', barcode='890123456790', name='Thermal Label Roll 4x6', reorder_threshold=20)
        db.session.add_all([p1, p2])
        db.session.flush()

        # Initial Bin Stocks
        stock1 = BinStock(bin_id=bin1.id, product_id=p1.id, quantity_on_hand=50, quantity_reserved=5)
        stock2 = BinStock(bin_id=bin2.id, product_id=p2.id, quantity_on_hand=120, quantity_reserved=0)
        db.session.add_all([stock1, stock2])

        db.session.commit()
        print("Database seeded with sample records successfully.")
    else:
        print("Database already contains records.")
