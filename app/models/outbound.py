from datetime import datetime
from app.extensions import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(25))
    billing_address = db.Column(db.String(255))
    orders = db.relationship('CustomerOrder', back_populates='client')

class CustomerOrder(db.Model):
    __tablename__ = 'customer_orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_status = db.Column(db.String(20), default='Pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('Client', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    packing_boxes = db.relationship('PackingBox', back_populates='order')
    shipments = db.relationship('Shipment', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_requested = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)

    order = db.relationship('CustomerOrder', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')
    pick_list_items = db.relationship('PickListItem', back_populates='order_item')

class PickList(db.Model):
    __tablename__ = 'pick_lists'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    picker_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Generated')
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    warehouse = db.relationship('Warehouse', back_populates='pick_lists')
    picker = db.relationship('User', back_populates='pick_lists')
    items = db.relationship('PickListItem', back_populates='pick_list', cascade='all, delete-orphan')

class PickListItem(db.Model):
    __tablename__ = 'pick_list_items'
    id = db.Column(db.Integer, primary_key=True)
    pick_list_id = db.Column(db.Integer, db.ForeignKey('pick_lists.id', ondelete='CASCADE'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('storage_bins.id'), nullable=False)
    quantity_to_pick = db.Column(db.Integer, nullable=False)
    quantity_picked = db.Column(db.Integer, default=0)
    is_picked = db.Column(db.Boolean, default=False)

    pick_list = db.relationship('PickList', back_populates='items')
    order_item = db.relationship('OrderItem', back_populates='pick_list_items')
    bin = db.relationship('StorageBin', back_populates='pick_list_items')

class PackingBox(db.Model):
    __tablename__ = 'packing_boxes'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id'), nullable=False)
    packer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    box_barcode = db.Column(db.String(60), unique=True, nullable=False)
    weight_kg = db.Column(db.Float, default=0.0)
    packed_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('CustomerOrder', back_populates='packing_boxes')
    packer = db.relationship('User', back_populates='packed_boxes')
