from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CustomerOrderCreateForm(FlaskForm):
    client_id = SelectField('Select Client', coerce=int, validators=[DataRequired()])
    order_number = StringField('Order Number (e.g. SO-2026-001)', validators=[DataRequired()])
    product_id = SelectField('Select Product', coerce=int, validators=[DataRequired()])
    quantity_requested = IntegerField('Quantity Requested', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Sales Price', default=0.0)
    submit = SubmitField('Create Outbound Order')
