"""Database models for the IPAM application."""
import ipaddress
from datetime import datetime
from decimal import Decimal

from flask import request
from flask_login import UserMixin, current_user
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Customer(db.Model):
    """Customer model for individual and corporate customers."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, default='individual')  # individual, company
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='customer', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    @property
    def active_assignments(self):
        """Get active assignments for this customer."""
        return self.assignments.filter_by(status='active').all()
    
    @property
    def total_assigned_ips(self):
        """Calculate total IPs assigned to this customer."""
        total = 0
        for assignment in self.active_assignments:
            if assignment.subnet:
                total += assignment.subnet.total_ips
        return total
    
    def to_dict(self):
        """Convert customer to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes,
            'active_assignments_count': len(self.active_assignments),
            'total_assigned_ips': self.total_assigned_ips
        }


class Subnet(db.Model):
    """Subnet model for IP subnet management."""
    __tablename__ = 'subnets'
    
    id = db.Column(db.Integer, primary_key=True)
    network_address = db.Column(db.String(45), nullable=False)  # IPv4 or IPv6
    prefix_length = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, assigned, reserved, quarantined
    location = db.Column(db.String(100))
    vlan_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_subnet_id = db.Column(db.Integer, db.ForeignKey('subnets.id'))
    auto_subdivide = db.Column(db.Boolean, default=False)
    is_subdivided = db.Column(db.Boolean, default=False)
    
    # Relationships
    parent = db.relationship('Subnet', remote_side=[id], backref='children')
    assignments = db.relationship('Assignment', backref='subnet', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_subnet_network_prefix', 'network_address', 'prefix_length'),
        db.Index('idx_subnet_status', 'status'),
    )
    
    def __repr__(self):
        return f'<Subnet {self.cidr}>'
    
    @property
    def cidr(self):
        """Get subnet in CIDR notation."""
        return f"{self.network_address}/{self.prefix_length}"
    
    @property
    def network(self):
        """Get ipaddress network object."""
        try:
            return ipaddress.ip_network(self.cidr)
        except ValueError:
            return None
    
    @property
    def total_ips(self):
        """Get total number of IPs in subnet."""
        network = self.network
        return network.num_addresses if network else 0
    
    @property
    def usable_ips(self):
        """Get number of usable IPs (excluding network and broadcast)."""
        network = self.network
        if network and network.version == 4 and network.prefixlen < 31:
            return network.num_addresses - 2
        return self.total_ips
    
    @hybrid_property
    def utilization(self):
        """Calculate subnet utilization percentage."""
        if self.status != 'available' or not self.children:
            return 100.0 if self.status == 'assigned' else 0.0
        
        assigned_ips = sum(child.total_ips for child in self.children 
                          if child.status == 'assigned')
        return (assigned_ips / self.total_ips * 100) if self.total_ips > 0 else 0.0
    
    def overlaps_with(self, other_cidr):
        """Check if this subnet overlaps with another CIDR."""
        try:
            this_network = self.network
            other_network = ipaddress.ip_network(other_cidr)
            return this_network.overlaps(other_network)
        except ValueError:
            return False
    
    def contains(self, ip_address):
        """Check if IP address is within this subnet."""
        try:
            network = self.network
            ip = ipaddress.ip_address(ip_address)
            return ip in network
        except ValueError:
            return False
    
    def to_dict(self):
        """Convert subnet to dictionary."""
        return {
            'id': self.id,
            'cidr': self.cidr,
            'network_address': self.network_address,
            'prefix_length': self.prefix_length,
            'status': self.status,
            'location': self.location,
            'vlan_id': self.vlan_id,
            'description': self.description,
            'total_ips': self.total_ips,
            'usable_ips': self.usable_ips,
            'utilization': round(self.utilization, 2),
            'parent_subnet_id': self.parent_subnet_id,
            'is_subdivided': self.is_subdivided,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Assignment(db.Model):
    """Assignment model for subnet-customer assignments."""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnets.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')  # USD, EUR, TRY
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    auto_renew = db.Column(db.Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_assignment_dates', 'start_date', 'end_date'),
        db.Index('idx_assignment_status', 'status'),
        db.Index('idx_assignment_customer', 'customer_id'),
        db.Index('idx_assignment_subnet', 'subnet_id'),
    )
    
    def __repr__(self):
        return f'<Assignment {self.subnet.cidr} to {self.customer.name}>'
    
    @property
    def is_expired(self):
        """Check if assignment has expired."""
        if self.end_date:
            return datetime.utcnow().date() > self.end_date
        return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining for assignment."""
        if self.end_date:
            delta = self.end_date - datetime.utcnow().date()
            return max(0, delta.days)
        return None
    
    def update_status(self):
        """Update assignment status based on dates."""
        if self.is_expired and self.status == 'active':
            self.status = 'expired'
            if self.subnet:
                self.subnet.status = 'available'
            db.session.commit()
    
    def to_dict(self):
        """Convert assignment to dictionary."""
        return {
            'id': self.id,
            'subnet_id': self.subnet_id,
            'subnet_cidr': self.subnet.cidr if self.subnet else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'price': float(self.price) if self.price else 0,
            'currency': self.currency,
            'status': self.status,
            'is_expired': self.is_expired,
            'days_remaining': self.days_remaining,
            'auto_renew': self.auto_renew,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExchangeRate(db.Model):
    """Exchange rate model for multi-currency support."""
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Numeric(12, 6), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_exchange_rate_currencies', 'from_currency', 'to_currency'),
    )
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency}/{self.to_currency}: {self.rate}>'
    
    @classmethod
    def get_rate(cls, from_currency, to_currency):
        """Get exchange rate between two currencies."""
        if from_currency == to_currency:
            return Decimal('1.0')
        
        rate = cls.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency
        ).first()
        
        return Decimal(str(rate.rate)) if rate else Decimal('1.0')
    
    def to_dict(self):
        """Convert exchange rate to dictionary."""
        return {
            'id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': float(self.rate),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AuditLog(db.Model):
    """Audit log model for tracking all system operations."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, login, logout
    entity_type = db.Column(db.String(50), nullable=False)  # subnet, customer, assignment, user
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_audit_timestamp', 'timestamp'),
        db.Index('idx_audit_user', 'user_id'),
        db.Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type} by user {self.user_id}>'
    
    @classmethod
    def log_action(cls, action, entity_type, entity_id=None, details=None):
        """Create an audit log entry."""
        if not current_user or not current_user.is_authenticated:
            return
        
        log = cls(
            user_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(log)
        db.session.commit()
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# SQLAlchemy event listeners for audit logging
@event.listens_for(Customer, 'after_insert')
def log_customer_insert(mapper, connection, target):
    """Log customer creation."""
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        AuditLog.log_action('create', 'customer', target.id, f'Created customer: {target.name}')


@event.listens_for(Customer, 'after_update')
def log_customer_update(mapper, connection, target):
    """Log customer update."""
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        AuditLog.log_action('update', 'customer', target.id, f'Updated customer: {target.name}')


@event.listens_for(Subnet, 'after_insert')
def log_subnet_insert(mapper, connection, target):
    """Log subnet creation."""
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        AuditLog.log_action('create', 'subnet', target.id, f'Created subnet: {target.cidr}')


@event.listens_for(Subnet, 'after_update')
def log_subnet_update(mapper, connection, target):
    """Log subnet update."""
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        AuditLog.log_action('update', 'subnet', target.id, f'Updated subnet: {target.cidr}')


@event.listens_for(Assignment, 'after_insert')
def log_assignment_insert(mapper, connection, target):
    """Log assignment creation."""
    @event.listens_for(db.session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        AuditLog.log_action('create', 'assignment', target.id, 
                           f'Assigned subnet {target.subnet_id} to customer {target.customer_id}')
