from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.extensions import db
from app.models.inbound import PurchaseOrder, PurchaseOrderItem, GoodsReceivedNote, GRNItem
from app.models.catalog import Supplier, Product
from app.models.facility import Warehouse, StorageBin
from app.models.inventory import BinStock
from app.forms.inbound_forms import PurchaseOrderCreateForm, ReceiveGRNForm, SupplierCreateForm

inbound_bp = Blueprint('inbound', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@inbound_bp.route('/suppliers')
@login_required
def supplier_list():
    suppliers = Supplier.query.all()
    return render_template('inbound/suppliers.html', suppliers=suppliers)

@inbound_bp.route('/suppliers/new', methods=['GET', 'POST'])
@login_required
def create_supplier():
    form = SupplierCreateForm()
    if form.validate_on_submit():
        existing = Supplier.query.filter_by(code=form.code.data).first()
        if existing:
            flash('Supplier with this code already exists.', 'danger')
            return render_template('inbound/create_supplier.html', form=form)

        supplier = Supplier(
            name=form.name.data,
            code=form.code.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            tax_number=form.tax_number.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash(f'Supplier {supplier.name} added successfully!', 'success')
        return redirect(url_for('inbound.supplier_list'))
    return render_template('inbound/create_supplier.html', form=form)

@inbound_bp.route('/orders')
@login_required
def po_list():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc()).all()
    return render_template('inbound/po_list.html', orders=orders)

@inbound_bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def create_po():
    suppliers = Supplier.query.all()
    if not suppliers:
        flash('No suppliers registered yet. Please add a supplier first.', 'warning')
        return redirect(url_for('inbound.create_supplier'))

    form = PurchaseOrderCreateForm()
    form.supplier_id.choices = [(s.id, f"{s.name} ({s.code})") for s in suppliers]
    form.warehouse_id.choices = [(w.id, f"{w.name} ({w.code})") for w in Warehouse.query.all()]
    form.product_id.choices = [(p.id, f"{p.sku} - {p.name}") for p in Product.query.all()]

    if form.validate_on_submit():
        try:
            po = PurchaseOrder(
                supplier_id=form.supplier_id.data,
                warehouse_id=form.warehouse_id.data,
                po_number=(form.po_number.data.strip() if getattr(form, 'po_number', None) and form.po_number.data else f'PO-20261111-3802'),
                status='Approved'
            )
            db.session.add(po)
            db.session.flush()

            po_item = PurchaseOrderItem(
                po_id=po.id,
                product_id=form.product_id.data,
                quantity_ordered=form.quantity_ordered.data,
                unit_price=form.unit_price.data
            )
            db.session.add(po_item)
            db.session.commit()

            flash(f'Purchase Order {po.po_number} generated successfully!', 'success')
            return redirect(url_for('inbound.po_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating PO: {str(e)}', 'danger')

    return render_template('inbound/create_po.html', form=form)

@inbound_bp.route('/orders/<int:po_id>/receive', methods=['GET', 'POST'])
@login_required
def receive_po(po_id):
    po = db.session.get(PurchaseOrder, po_id)
    if not po or not po.items:
        flash('Purchase Order not found or has no line items.', 'danger')
        return redirect(url_for('inbound.po_list'))

    po_item = po.items[0]
    form = ReceiveGRNForm()
    form.destination_bin_id.choices = [(b.id, f"{b.bin_barcode} (Shelf {b.shelf_id})") for b in StorageBin.query.all()]

    if form.validate_on_submit():
        try:
            grn_num = f"GRN-{po.po_number}-{int(datetime.utcnow().timestamp())}"
            grn = GoodsReceivedNote(
                po_id=po.id,
                grn_number=grn_num,
                received_by_user_id=session['user_id'],
                status='Completed'
            )
            db.session.add(grn)
            db.session.flush()

            grn_item = GRNItem(
                grn_id=grn.id,
                po_item_id=po_item.id,
                quantity_received=form.quantity_received.data,
                quantity_rejected=form.quantity_rejected.data
            )
            db.session.add(grn_item)

            stock = BinStock.query.filter_by(
                bin_id=form.destination_bin_id.data,
                product_id=po_item.product_id
            ).first()

            if stock:
                stock.quantity_on_hand += form.quantity_received.data
            else:
                stock = BinStock(
                    bin_id=form.destination_bin_id.data,
                    product_id=po_item.product_id,
                    quantity_on_hand=form.quantity_received.data,
                    quantity_reserved=0
                )
                db.session.add(stock)

            po.status = 'Received'
            db.session.commit()

            flash(f'Inventory received via {grn_num} and added to storage bin.', 'success')
            return redirect(url_for('inventory.stock_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error receiving goods: {str(e)}', 'danger')

    return render_template('inbound/receive_po.html', po=po, po_item=po_item, form=form)
