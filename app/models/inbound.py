from datetime import datetime
from app.extensions import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Draft')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    warehouse = db.relationship('Warehouse', back_populates='purchase_orders')
    items = db.relationship('PurchaseOrderItem', back_populates='purchase_order', cascade='all, delete-orphan')
    grns = db.relationship('GoodsReceivedNote', back_populates='purchase_order')

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)

    purchase_order = db.relationship('PurchaseOrder', back_populates='items')
    product = db.relationship('Product', back_populates='po_items')
    grn_items = db.relationship('GRNItem', back_populates='po_item')

class GoodsReceivedNote(db.Model):
    __tablename__ = 'goods_received_notes'
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    received_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Received')

    purchase_order = db.relationship('PurchaseOrder', back_populates='grns')
    receiver = db.relationship('User', back_populates='grns_received')
    items = db.relationship('GRNItem', back_populates='grn', cascade='all, delete-orphan')

class GRNItem(db.Model):
    __tablename__ = 'grn_items'
    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_received_notes.id', ondelete='CASCADE'), nullable=False)
    po_item_id = db.Column(db.Integer, db.ForeignKey('purchase_order_items.id'), nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    quantity_rejected = db.Column(db.Integer, default=0)

    grn = db.relationship('GoodsReceivedNote', back_populates='items')
    po_item = db.relationship('PurchaseOrderItem', back_populates='grn_items')
    inspections = db.relationship('QualityInspection', back_populates='grn_item', cascade='all, delete-orphan')

class QualityInspection(db.Model):
    __tablename__ = 'quality_inspections'
    id = db.Column(db.Integer, primary_key=True)
    grn_item_id = db.Column(db.Integer, db.ForeignKey('grn_items.id', ondelete='CASCADE'), nullable=False)
    inspected_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    passed_qty = db.Column(db.Integer, default=0)
    failed_qty = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(255))
    inspected_at = db.Column(db.DateTime, default=datetime.utcnow)

    grn_item = db.relationship('GRNItem', back_populates='inspections')
    inspector = db.relationship('User', back_populates='inspections')

class PutawayTask(db.Model):
    __tablename__ = 'putaway_tasks'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    warehouse = db.relationship('Warehouse', back_populates='putaway_tasks')
    assignee = db.relationship('User', back_populates='putaway_tasks')
    items = db.relationship('PutawayItem', back_populates='task', cascade='all, delete-orphan')

class PutawayItem(db.Model):
    __tablename__ = 'putaway_items'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('putaway_tasks.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    source_dock = db.Column(db.String(50), default='Dock-1')
    destination_bin_id = db.Column(db.Integer, db.ForeignKey('storage_bins.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    task = db.relationship('PutawayTask', back_populates='items')
    product = db.relationship('Product', back_populates='putaway_items')
    destination_bin = db.relationship('StorageBin', back_populates='putaway_items')
