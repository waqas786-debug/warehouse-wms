from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email

class SupplierCreateForm(FlaskForm):
    name = StringField('Supplier Company Name', validators=[DataRequired()])
    code = StringField('Supplier Code (e.g. SUP-001)', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    tax_number = StringField('Tax / NTN Number')
    submit = SubmitField('Register Supplier')

class PurchaseOrderCreateForm(FlaskForm):
    supplier_id = SelectField('Supplier', coerce=int, validators=[DataRequired()])
    warehouse_id = SelectField('Destination Warehouse', coerce=int, validators=[DataRequired()])
    po_number = StringField('PO Number', validators=[DataRequired()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_ordered = IntegerField('Quantity Ordered', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', default=0.0)
    submit = SubmitField('Create Purchase Order')

class ReceiveGRNForm(FlaskForm):
    quantity_received = IntegerField('Quantity Received (Good)', validators=[DataRequired(), NumberRange(min=0)])
    quantity_rejected = IntegerField('Quantity Rejected (Damaged)', default=0, validators=[NumberRange(min=0)])
    destination_bin_id = SelectField('Putaway Storage Bin', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Accept & Receive Inventory')
