from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.extensions import db
from app.models.models import CustomerOrder, OrderItem, Product, Client
from app.models.auth import User
from datetime import datetime

portal_bp = Blueprint('portal', __name__)

@portal_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    client = Client.query.filter_by(email=user.email).first() if user else None
    
    orders = []
    if client:
        orders = CustomerOrder.query.filter_by(client_id=client.id).order_by(CustomerOrder.order_date.desc()).all()
    elif user:
        # Fallback agar client record alag se na mila ho toh generic first client check karein
        client = Client.query.first()
        if client:
            orders = CustomerOrder.query.filter_by(client_id=client.id).order_by(CustomerOrder.order_date.desc()).all()

    return render_template('portal/dashboard.html', orders=orders, client=client)

@portal_bp.route('/order/new', methods=['GET', 'POST'])
def create_order():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    client = Client.query.filter_by(email=user.email).first() if user else None
    if not client:
        client = Client.query.first()

    products = Product.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        qty = int(request.form.get('quantity', 1))
        shipping_addr = request.form.get('shipping_address')

        product = Product.query.get(product_id)
        unit_price = 1500.0

        new_order = CustomerOrder(
            order_number=f"ORD-{datetime.utcnow().strftime('%y%m%d%H%M')}",
            client_id=client.id if client else None,
            order_status='PENDING',
            payment_status='UNPAID',
            shipping_address=shipping_addr,
            order_date=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.flush()

        item = OrderItem(
            order_id=new_order.id,
            product_id=product.id if product else product_id,
            quantity=qty,
            unit_price=unit_price,
            line_total=unit_price * qty
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Order successfully placed! Warehouse team will process it shortly.', 'success')
        return redirect(url_for('portal.dashboard'))

    return render_template('portal/create_order.html', products=products)