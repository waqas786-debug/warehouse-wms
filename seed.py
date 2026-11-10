from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.auth import Role, User, StaffProfile
from app.models.facility import Warehouse, Zone, Aisle, Rack, Shelf, StorageBin
from app.models.catalog import ProductCategory, UnitOfMeasure, Product
from app.models.inventory import BinStock
from app.models.outbound import Client

app = create_app()

with app.app_context():
    print("Initializing database and verifying tables...")
    db.create_all()

    table_count = len(db.metadata.tables.keys())
    print(f"Total Registered Tables: {table_count}")

    # -------------------------------------------------------------
    # 1. CORE WMS SETUP (If fresh database)
    # -------------------------------------------------------------
    if not Role.query.filter_by(name='Administrator').first():
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
        print("Base warehouse data seeded successfully.")

    # -------------------------------------------------------------
    # 2. CLIENT ROLE & CUSTOMER PORTAL SEEDING
    # -------------------------------------------------------------
    client_role = Role.query.filter_by(name='Client').first()
    if not client_role:
        client_role = Role(name='Client', description='External customer / client access')
        db.session.add(client_role)
        db.session.flush()
        print("Created Role: Client")

    demo_client = Client.query.filter_by(email='customer1@enterprise.com').first()
    if not demo_client:
        demo_client = Client(
            company_name="Alpha Retailers Ltd",
            contact_name="Customer One",
            email="customer1@enterprise.com",
            phone="+923001234567",
            address="Commercial Market, Lahore",
            is_active=True
        )
        db.session.add(demo_client)
        db.session.flush()
        print("Created Client record: Alpha Retailers Ltd")

    customer_user = User.query.filter_by(username='customer1').first()
    if not customer_user:
        customer_user = User(
            role_id=client_role.id,
            username='customer1',
            email='customer1@enterprise.com',
            password_hash=generate_password_hash('customer123'),
            is_active=True
        )
        db.session.add(customer_user)
        print("Created User: customer1 (Password: customer123)")

    db.session.commit()
    print("Database seeding completed successfully.")