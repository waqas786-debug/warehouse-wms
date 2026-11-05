from app.extensions import db

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255))
    total_capacity_sqft = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

    zones = db.relationship('Zone', back_populates='warehouse', cascade='all, delete-orphan')
    purchase_orders = db.relationship('PurchaseOrder', back_populates='warehouse')
    putaway_tasks = db.relationship('PutawayTask', back_populates='warehouse')
    pallets = db.relationship('Pallet', back_populates='warehouse')
    stock_adjustments = db.relationship('StockAdjustment', back_populates='warehouse')
    pick_lists = db.relationship('PickList', back_populates='warehouse')
    vehicles = db.relationship('DeliveryVehicle', back_populates='warehouse')

class Zone(db.Model):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    zone_type = db.Column(db.String(50), default='General')

    warehouse = db.relationship('Warehouse', back_populates='zones')
    aisles = db.relationship('Aisle', back_populates='zone', cascade='all, delete-orphan')

class Aisle(db.Model):
    __tablename__ = 'aisles'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id', ondelete='CASCADE'), nullable=False)
    aisle_code = db.Column(db.String(20), nullable=False)
    width_meters = db.Column(db.Float, default=2.5)

    zone = db.relationship('Zone', back_populates='aisles')
    racks = db.relationship('Rack', back_populates='aisle', cascade='all, delete-orphan')

class Rack(db.Model):
    __tablename__ = 'racks'
    id = db.Column(db.Integer, primary_key=True)
    aisle_id = db.Column(db.Integer, db.ForeignKey('aisles.id', ondelete='CASCADE'), nullable=False)
    rack_code = db.Column(db.String(20), nullable=False)
    max_weight_capacity = db.Column(db.Float, default=1000.0)

    aisle = db.relationship('Aisle', back_populates='racks')
    shelves = db.relationship('Shelf', back_populates='rack', cascade='all, delete-orphan')

class Shelf(db.Model):
    __tablename__ = 'shelves'
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id', ondelete='CASCADE'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)
    height_meters = db.Column(db.Float, default=1.5)

    rack = db.relationship('Rack', back_populates='shelves')
    bins = db.relationship('StorageBin', back_populates='shelf', cascade='all, delete-orphan')

class StorageBin(db.Model):
    __tablename__ = 'storage_bins'
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id', ondelete='CASCADE'), nullable=False)
    bin_barcode = db.Column(db.String(50), unique=True, nullable=False)
    max_volume_cbm = db.Column(db.Float, default=0.5)
    is_occupied = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

    shelf = db.relationship('Shelf', back_populates='bins')
    bin_stocks = db.relationship('BinStock', back_populates='bin', cascade='all, delete-orphan')
    putaway_items = db.relationship('PutawayItem', back_populates='destination_bin')
    pallet = db.relationship('Pallet', back_populates='current_bin', uselist=False)
    adjustment_items = db.relationship('StockAdjustmentItem', back_populates='bin')
    pick_list_items = db.relationship('PickListItem', back_populates='bin')
