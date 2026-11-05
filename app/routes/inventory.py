from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.extensions import db
from app.models.facility import StorageBin, Warehouse
from app.models.catalog import Product
from app.models.inventory import BinStock, StockAdjustment, StockAdjustmentItem
from app.forms.inventory_forms import StockAdjustmentForm

inventory_bp = Blueprint('inventory', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@inventory_bp.route('/dashboard')
@login_required
def dashboard():
    total_products = Product.query.count()
    total_warehouses = Warehouse.query.count()
    low_stock_items = db.session.query(Product).join(BinStock).filter(
        BinStock.quantity_on_hand <= Product.reorder_threshold
    ).distinct().count()

    recent_adjustments = StockAdjustment.query.order_by(
        StockAdjustment.created_at.desc()
    ).limit(5).all()

    return render_template(
        'inventory/dashboard.html',
        total_products=total_products,
        total_warehouses=total_warehouses,
        low_stock_items=low_stock_items,
        recent_adjustments=recent_adjustments
    )

@inventory_bp.route('/stocks')
@login_required
def stock_list():
    stocks = BinStock.query.join(StorageBin).join(Product).all()
    return render_template('inventory/stock_list.html', stocks=stocks)

@inventory_bp.route('/adjust', methods=['GET', 'POST'])
@login_required
def adjust_stock():
    form = StockAdjustmentForm()
    form.bin_id.choices = [(b.id, f"{b.bin_barcode} (Shelf {b.shelf_id})") for b in StorageBin.query.all()]
    form.product_id.choices = [(p.id, f"{p.sku} - {p.name}") for p in Product.query.all()]

    if form.validate_on_submit():
        try:
            bin_obj = db.session.get(StorageBin, form.bin_id.data)
            warehouse_id = bin_obj.shelf.rack.aisle.zone.warehouse_id

            adjustment = StockAdjustment(
                warehouse_id=warehouse_id,
                approved_by_user_id=session['user_id'],
                reason_code=form.reason_code.data
            )
            db.session.add(adjustment)
            db.session.flush()

            adjustment_item = StockAdjustmentItem(
                adjustment_id=adjustment.id,
                bin_id=form.bin_id.data,
                product_id=form.product_id.data,
                quantity_change=form.quantity_change.data,
                notes=form.notes.data
            )
            db.session.add(adjustment_item)

            stock_record = BinStock.query.filter_by(
                bin_id=form.bin_id.data,
                product_id=form.product_id.data
            ).first()

            if stock_record:
                stock_record.quantity_on_hand += form.quantity_change.data
                if stock_record.quantity_on_hand < 0:
                    stock_record.quantity_on_hand = 0
            else:
                new_qty = max(0, form.quantity_change.data)
                stock_record = BinStock(
                    bin_id=form.bin_id.data,
                    product_id=form.product_id.data,
                    quantity_on_hand=new_qty,
                    quantity_reserved=0
                )
                db.session.add(stock_record)

            db.session.commit()
            flash('Inventory adjustment applied successfully.', 'success')
            return redirect(url_for('inventory.stock_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error applying adjustment: {str(e)}', 'danger')

    return render_template('inventory/adjust_stock.html', form=form)
