from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.extensions import db
from app.models.fleet import ShippingCarrier, Shipment, DeliveryVehicle, DispatchManifest, ProofOfDelivery
from app.models.outbound import CustomerOrder
from app.forms.fleet_forms import ShipmentDispatchForm, ProofOfDeliveryForm

fleet_bp = Blueprint('fleet', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@fleet_bp.route('/shipments')
@login_required
def shipment_list():
    shipments = Shipment.query.order_by(Shipment.dispatched_at.desc()).all()
    carriers = ShippingCarrier.query.all()
    vehicles = DeliveryVehicle.query.all()
    return render_template('fleet/shipment_list.html', shipments=shipments, carriers=carriers, vehicles=vehicles)

@fleet_bp.route('/dispatch', methods=['GET', 'POST'])
@login_required
def dispatch_order():
    # Only show orders that are Dispatched from warehouse but don't have a shipment tracking yet
    dispatched_orders = CustomerOrder.query.filter_by(order_status='Dispatched').all()
    eligible_orders = [o for o in dispatched_orders if not o.shipments]

    if not eligible_orders:
        flash('No fulfilled orders waiting for carrier dispatch.', 'warning')
        return redirect(url_for('fleet.shipment_list'))

    form = ShipmentDispatchForm()
    form.order_id.choices = [(o.id, f"{o.order_number} ({o.client.company_name})") for o in eligible_orders]
    form.carrier_id.choices = [(c.id, f"{c.name} - {c.service_type}") for c in ShippingCarrier.query.all()]
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.driver_name})") for v in DeliveryVehicle.query.all()]

    if form.validate_on_submit():
        existing = Shipment.query.filter_by(tracking_number=form.tracking_number.data).first()
        if existing:
            flash('Tracking number already exists. Please enter a unique tracking code.', 'danger')
            return render_template('fleet/dispatch_form.html', form=form)

        try:
            # 1. Create Manifest
            manifest = DispatchManifest(
                vehicle_id=form.vehicle_id.data,
                manifest_number=f"MNF-{int(datetime.utcnow().timestamp())}",
                departure_time=datetime.utcnow(),
                status='In-Transit'
            )
            db.session.add(manifest)

            # 2. Create Shipment
            shipment = Shipment(
                order_id=form.order_id.data,
                carrier_id=form.carrier_id.data,
                tracking_number=form.tracking_number.data,
                dispatched_at=datetime.utcnow()
            )
            db.session.add(shipment)
            db.session.commit()

            flash(f'Shipment created with Tracking #{shipment.tracking_number} under Manifest #{manifest.manifest_number}.', 'success')
            return redirect(url_for('fleet.shipment_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating shipment: {str(e)}', 'danger')

    return render_template('fleet/dispatch_form.html', form=form)

@fleet_bp.route('/shipments/<int:shipment_id>/pod', methods=['GET', 'POST'])
@login_required
def confirm_pod(shipment_id):
    shipment = db.session.get(Shipment, shipment_id)
    if not shipment:
        flash('Shipment record not found.', 'danger')
        return redirect(url_for('fleet.shipment_list'))

    if shipment.pod:
        flash('Proof of Delivery (POD) already recorded for this consignment.', 'info')
        return redirect(url_for('fleet.shipment_list'))

    form = ProofOfDeliveryForm()
    if form.validate_on_submit():
        try:
            pod = ProofOfDelivery(
                shipment_id=shipment.id,
                recipient_name=form.recipient_name.data,
                status=form.status.data,
                delivered_at=datetime.utcnow()
            )
            db.session.add(pod)

            # Mark order as Completed if delivered
            if form.status.data == 'Delivered':
                shipment.order.order_status = 'Completed'

            db.session.commit()
            flash(f'POD recorded! Order #{shipment.order.order_number} marked as {form.status.data}.', 'success')
            return redirect(url_for('fleet.shipment_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging POD: {str(e)}', 'danger')

    return render_template('fleet/pod_form.html', shipment=shipment, form=form)
