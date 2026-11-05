from datetime import datetime
from app.extensions import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship('User', back_populates='role')
    role_permissions = db.relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    module = db.Column(db.String(50), nullable=False)
    role_permissions = db.relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
    role = db.relationship('Role', back_populates='role_permissions')
    permission = db.relationship('Permission', back_populates='role_permissions')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', back_populates='users')
    profile = db.relationship('StaffProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    activity_logs = db.relationship('UserActivityLog', back_populates='user', cascade='all, delete-orphan')
    grns_received = db.relationship('GoodsReceivedNote', back_populates='receiver')
    inspections = db.relationship('QualityInspection', back_populates='inspector')
    putaway_tasks = db.relationship('PutawayTask', back_populates='assignee')
    stock_adjustments = db.relationship('StockAdjustment', back_populates='approver')
    pick_lists = db.relationship('PickList', back_populates='picker')
    packed_boxes = db.relationship('PackingBox', back_populates='packer')

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    cnic_or_id = db.Column(db.String(30))
    shift_type = db.Column(db.String(20), default='Morning')
    user = db.relationship('User', back_populates='profile')

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    endpoint = db.Column(db.String(150))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='activity_logs')
