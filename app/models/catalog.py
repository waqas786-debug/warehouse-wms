from app.extensions import db

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    parent = db.relationship('ProductCategory', remote_side=[id], backref='subcategories')
    products = db.relationship('Product', back_populates='category')

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    contact_person = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(25))
    tax_number = db.Column(db.String(50))
    supplier_products = db.relationship('SupplierProduct', back_populates='supplier', cascade='all, delete-orphan')
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier')

class UnitOfMeasure(db.Model):
    __tablename__ = 'units_of_measure'
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(50), nullable=False)
    abbreviation = db.Column(db.String(10), unique=True, nullable=False)
    products = db.relationship('Product', back_populates='uom')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    uom_id = db.Column(db.Integer, db.ForeignKey('units_of_measure.id'), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    weight_kg = db.Column(db.Float, default=0.0)
    dimensions_cm = db.Column(db.String(50))
    reorder_threshold = db.Column(db.Integer, default=10)

    category = db.relationship('ProductCategory', back_populates='products')
    uom = db.relationship('UnitOfMeasure', back_populates='products')
    variants = db.relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')
    supplier_mappings = db.relationship('SupplierProduct', back_populates='product', cascade='all, delete-orphan')
    po_items = db.relationship('PurchaseOrderItem', back_populates='product')
    putaway_items = db.relationship('PutawayItem', back_populates='product')
    batches = db.relationship('InventoryBatch', back_populates='product', cascade='all, delete-orphan')
    stocks = db.relationship('BinStock', back_populates='product', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product')
    adjustment_items = db.relationship('StockAdjustmentItem', back_populates='product')

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    variant_sku = db.Column(db.String(60), unique=True, nullable=False)
    attribute_values = db.Column(db.String(255))
    product = db.relationship('Product', back_populates='variants')

class SupplierProduct(db.Model):
    __tablename__ = 'supplier_products'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    supplier_sku = db.Column(db.String(50))
    cost_price = db.Column(db.Float, default=0.0)
    lead_time_days = db.Column(db.Integer, default=1)
    supplier = db.relationship('Supplier', back_populates='supplier_products')
    product = db.relationship('Product', back_populates='supplier_mappings')
