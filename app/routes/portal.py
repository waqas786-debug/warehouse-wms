from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.extensions import db
from app.models.outbound import CustomerOrder, OrderItem, Client
from app.models.catalog import Product
from app.models.auth import User
from datetime import datetime

portal_bp = Blueprint("portal", __name__)

def get_or_create_client(user):
    # 1. Search by email if user has one
    if user and user.email:
        client = Client.query.filter_by(email=user.email).first()
        if client:
            return client

    # 2. Get first client if any exists
    client = Client.query.first()
    if client:
        return client

    # 3. Create default client with exact schema fields
    client = Client(
        client_name=user.username if user else "Customer One",
        company_name="Alpha Retailers Ltd",
        email=user.email if (user and user.email) else "customer1@enterprise.com",
        phone="+923001234567",
        billing_address="Commercial Market, Lahore"
    )
    db.session.add(client)
    db.session.commit()
    return client

@portal_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    client = get_or_create_client(user)

    orders = CustomerOrder.query.filter_by(client_id=client.id).order_by(CustomerOrder.id.desc()).all()
    return render_template("portal/dashboard.html", orders=orders, client=client)

@portal_bp.route("/order/new", methods=["GET", "POST"])
def create_order():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    client = get_or_create_client(user)
    products = Product.query.all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        qty = int(request.form.get("quantity", 1))

        order_no = f"ORD-{datetime.utcnow().strftime('%y%m%d%H%M%S')}"

        # 1. Create Order with non-null client_id
        new_order = CustomerOrder(
            order_number=order_no,
            client_id=client.id,
            order_status="PENDING",
            order_date=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.commit()

        # 2. Create Order Item
        item = OrderItem(
            order_id=new_order.id,
            product_id=int(product_id),
            quantity_requested=qty,
            unit_price=1500.0
        )
        db.session.add(item)
        db.session.commit()

        flash(f"Order {order_no} placed successfully! Warehouse dispatch team notified.", "success")
        return redirect(url_for("portal.dashboard"))

    return render_template("portal/create_order.html", products=products)
