from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.extensions import db
from app.models.outbound import Client, CustomerOrder, OrderItem, PickList, PickListItem
from app.models.catalog import Product
from app.models.inventory import BinStock
from app.models.facility import Warehouse
from app.forms.outbound_forms import CustomerOrderCreateForm

outbound_bp = Blueprint('outbound', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@outbound_bp.route('/orders')
@login_required
def order_list():
    orders = CustomerOrder.query.order_by(CustomerOrder.order_date.desc()).all()
    return render_template('outbound/order_list.html', orders=orders)

@outbound_bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def create_order():
    clients = Client.query.all()
    products = Product.query.all()

    if not clients:
        flash('No clients found. Please make sure clients exist in database.', 'warning')
        return redirect(url_for('outbound.order_list'))

    form = CustomerOrderCreateForm()
    form.client_id.choices = [(c.id, f"{c.company_name} ({c.client_name})") for c in clients]
    form.product_id.choices = [(p.id, f"{p.sku} - {p.name}") for p in products]

    if request.method == 'POST':
        if form.validate_on_submit():
            existing = CustomerOrder.query.filter_by(order_number=form.order_number.data).first()
            if existing:
                flash(f"Order number '{form.order_number.data}' already exists! Enter a unique order number.", 'danger')
                return render_template('outbound/create_order.html', form=form)

            try:
                order = CustomerOrder(
                    client_id=form.client_id.data,
                    order_number=form.order_number.data.strip(),
                    order_status='Pending'
                )
                db.session.add(order)
                db.session.flush()

                item = OrderItem(
                    order_id=order.id,
                    product_id=form.product_id.data,
                    quantity_requested=form.quantity_requested.data,
                    unit_price=form.unit_price.data
                )
                db.session.add(item)
                db.session.commit()

                flash(f'Outbound Order {order.order_number} created successfully.', 'success')
                return redirect(url_for('outbound.order_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating order: {str(e)}', 'danger')
        else:
            flash('Form submission failed. Please check the highlighted inputs.', 'danger')

    return render_template('outbound/create_order.html', form=form)

@outbound_bp.route('/orders/<int:order_id>/fulfill', methods=['POST'])
@login_required
def fulfill_order(order_id):
    order = db.session.get(CustomerOrder, order_id)
    if not order or not order.items:
        flash('Order not found or has no line items.', 'danger')
        return redirect(url_for('outbound.order_list'))

    item = order.items[0]
    bin_stock = BinStock.query.filter_by(product_id=item.product_id).filter(BinStock.quantity_on_hand >= item.quantity_requested).first()

    if not bin_stock:
        flash(f'Insufficient stock! Required: {item.quantity_requested} units, but not enough quantity available in any single bin.', 'danger')
        return redirect(url_for('outbound.order_list'))

    try:
        wh = Warehouse.query.first()
        pick_list = PickList(
            warehouse_id=wh.id,
            picker_user_id=session['user_id'],
            status='Completed'
        )
        db.session.add(pick_list)
        db.session.flush()

        pick_item = PickListItem(
            pick_list_id=pick_list.id,
            order_item_id=item.id,
            bin_id=bin_stock.bin_id,
            quantity_to_pick=item.quantity_requested,
            quantity_picked=item.quantity_requested,
            is_picked=True
        )
        db.session.add(pick_item)

        bin_stock.quantity_on_hand -= item.quantity_requested
        order.order_status = 'Dispatched'

        db.session.commit()
        flash(f'Order {order.order_number} picked and dispatched! {item.quantity_requested} units deducted from bin.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error fulfilling order: {str(e)}', 'danger')

    return redirect(url_for('outbound.order_list'))
