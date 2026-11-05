from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ShipmentDispatchForm(FlaskForm):
    order_id = SelectField('Select Dispatched Order', coerce=int, validators=[DataRequired()])
    carrier_id = SelectField('Shipping Carrier', coerce=int, validators=[DataRequired()])
    vehicle_id = SelectField('Assign Fleet Vehicle', coerce=int, validators=[DataRequired()])
    tracking_number = StringField('Tracking AWB Number (e.g. TRK-78901)', validators=[DataRequired()])
    submit = SubmitField('Generate Dispatch Manifest & Tracking')

class ProofOfDeliveryForm(FlaskForm):
    recipient_name = StringField('Recipient Signature Name', validators=[DataRequired()])
    status = SelectField('Delivery Status', choices=[
        ('Delivered', 'Delivered & Accepted'),
        ('Returned', 'Delivery Attempt Failed / Return to Origin')
    ], validators=[DataRequired()])
    submit = SubmitField('Confirm Proof of Delivery (POD)')
