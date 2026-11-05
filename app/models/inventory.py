from datetime import datetime
from app.extensions import db

class InventoryBatch(db.Model):
    __tablename__ = 'inventory_batches'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    mfg_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)

    product = db.relationship('Product', back_populates='batches')
    bin_stocks = db.relationship('BinStock', back_populates='batch')
    pallet_contents = db.relationship('PalletContent', back_populates='batch')

class BinStock(db.Model):
    __tablename__ = 'bin_stocks'
    id = db.Column(db.Integer, primary_key=True)
    bin_id = db.Column(db.Integer, db.ForeignKey('storage_bins.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=True)
    quantity_on_hand = db.Column(db.Integer, default=0, nullable=False)
    quantity_reserved = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bin = db.relationship('StorageBin', back_populates='bin_stocks')
    product = db.relationship('Product', back_populates='stocks')
    batch = db.relationship('InventoryBatch', back_populates='bin_stocks')

class Pallet(db.Model):
    __tablename__ = 'pallets'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    pallet_barcode = db.Column(db.String(50), unique=True, nullable=False)
    pallet_type = db.Column(db.String(30), default='Wooden Standard')
    current_bin_id = db.Column(db.Integer, db.ForeignKey('storage_bins.id'), nullable=True)

    warehouse = db.relationship('Warehouse', back_populates='pallets')
    current_bin = db.relationship('StorageBin', back_populates='pallet')
    contents = db.relationship('PalletContent', back_populates='pallet', cascade='all, delete-orphan')

class PalletContent(db.Model):
    __tablename__ = 'pallet_contents'
    id = db.Column(db.Integer, primary_key=True)
    pallet_id = db.Column(db.Integer, db.ForeignKey('pallets.id', ondelete='CASCADE'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    pallet = db.relationship('Pallet', back_populates='contents')
    batch = db.relationship('InventoryBatch', back_populates='pallet_contents')

class StockAdjustment(db.Model):
    __tablename__ = 'stock_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason_code = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    warehouse = db.relationship('Warehouse', back_populates='stock_adjustments')
    approver = db.relationship('User', back_populates='stock_adjustments')
    items = db.relationship('StockAdjustmentItem', back_populates='adjustment', cascade='all, delete-orphan')

class StockAdjustmentItem(db.Model):
    __tablename__ = 'stock_adjustment_items'
    id = db.Column(db.Integer, primary_key=True)
    adjustment_id = db.Column(db.Integer, db.ForeignKey('stock_adjustments.id', ondelete='CASCADE'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('storage_bins.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255))

    adjustment = db.relationship('StockAdjustment', back_populates='items')
    bin = db.relationship('StorageBin', back_populates='adjustment_items')
    product = db.relationship('Product', back_populates='adjustment_items')
