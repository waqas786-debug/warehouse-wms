from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class StockAdjustmentForm(FlaskForm):
    bin_id = SelectField('Select Storage Bin', coerce=int, validators=[DataRequired()])
    product_id = SelectField('Select Product', coerce=int, validators=[DataRequired()])
    quantity_change = IntegerField('Quantity Delta (+/-)', validators=[DataRequired()])
    reason_code = SelectField('Reason', choices=[
        ('CYCLE_COUNT', 'Cycle Count Variance'),
        ('DAMAGED', 'Damaged Stock'),
        ('EXPIRED', 'Expired Batch'),
        ('MANUAL_CORRECTION', 'Manual Correction')
    ], validators=[DataRequired()])
    notes = TextAreaField('Audit Notes')
    submit = SubmitField('Commit Stock Adjustment')
