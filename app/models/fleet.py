from datetime import datetime
from app.extensions import db

class ShippingCarrier(db.Model):
    __tablename__ = 'shipping_carriers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), default='Express')
    contact_number = db.Column(db.String(25))
    shipments = db.relationship('Shipment', back_populates='carrier')

class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id'), nullable=False)
    carrier_id = db.Column(db.Integer, db.ForeignKey('shipping_carriers.id'), nullable=False)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False)
    shipping_label_url = db.Column(db.String(255))
    dispatched_at = db.Column(db.DateTime, nullable=True)

    order = db.relationship('CustomerOrder', back_populates='shipments')
    carrier = db.relationship('ShippingCarrier', back_populates='shipments')
    pod = db.relationship('ProofOfDelivery', back_populates='shipment', uselist=False, cascade='all, delete-orphan')

class DeliveryVehicle(db.Model):
    __tablename__ = 'delivery_vehicles'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    vehicle_number = db.Column(db.String(30), unique=True, nullable=False)
    model = db.Column(db.String(50))
    driver_name = db.Column(db.String(80))
    driver_phone = db.Column(db.String(25))

    warehouse = db.relationship('Warehouse', back_populates='vehicles')
    manifests = db.relationship('DispatchManifest', back_populates='vehicle')

class DispatchManifest(db.Model):
    __tablename__ = 'dispatch_manifests'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('delivery_vehicles.id'), nullable=False)
    manifest_number = db.Column(db.String(50), unique=True, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Loading')

    vehicle = db.relationship('DeliveryVehicle', back_populates='manifests')

class ProofOfDelivery(db.Model):
    __tablename__ = 'proof_of_deliveries'
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id', ondelete='CASCADE'), unique=True, nullable=False)
    recipient_name = db.Column(db.String(80), nullable=False)
    signature_image_path = db.Column(db.String(255))
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Delivered')

    shipment = db.relationship('Shipment', back_populates='pod')
