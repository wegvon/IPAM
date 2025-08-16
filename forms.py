"""WTForms for the IPAM application."""
import ipaddress
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField, 
                     TextAreaField, IntegerField, DecimalField, DateField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, NumberRange

from app.models import User, Customer, Subnet


class LoginForm(FlaskForm):
    """Login form for user authentication."""
    username = StringField('Kullanıcı Adı', validators=[DataRequired(message='Kullanıcı adı gerekli')])
    password = PasswordField('Şifre', validators=[DataRequired(message='Şifre gerekli')])
    remember_me = BooleanField('Beni Hatırla')


class UserForm(FlaskForm):
    """Form for creating/editing users."""
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Kullanıcı adı gerekli'),
        Length(min=3, max=64, message='Kullanıcı adı 3-64 karakter olmalı')
    ])
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta gerekli'),
        Email(message='Geçerli bir e-posta adresi girin')
    ])
    password = PasswordField('Şifre', validators=[
        Length(min=6, message='Şifre en az 6 karakter olmalı')
    ])
    is_admin = BooleanField('Yönetici')
    is_active = BooleanField('Aktif')

    def validate_username(self, field):
        """Check if username already exists."""
        if hasattr(self, 'user_id'):
            user = User.query.filter_by(username=field.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Bu kullanıcı adı zaten kullanımda')
        else:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Bu kullanıcı adı zaten kullanımda')

    def validate_email(self, field):
        """Check if email already exists."""
        if hasattr(self, 'user_id'):
            user = User.query.filter_by(email=field.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Bu e-posta adresi zaten kullanımda')
        else:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Bu e-posta adresi zaten kullanımda')


class CustomerForm(FlaskForm):
    """Form for creating/editing customers."""
    name = StringField('Müşteri Adı', validators=[
        DataRequired(message='Müşteri adı gerekli'),
        Length(max=255, message='Müşteri adı çok uzun')
    ])
    type = SelectField('Müşteri Tipi', choices=[
        ('individual', 'Bireysel'),
        ('company', 'Kurumsal')
    ], validators=[DataRequired(message='Müşteri tipi seçin')])
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta gerekli'),
        Email(message='Geçerli bir e-posta adresi girin')
    ])
    phone = StringField('Telefon', validators=[
        Optional(),
        Length(max=20, message='Telefon numarası çok uzun')
    ])
    address = TextAreaField('Adres', validators=[Optional()])
    status = SelectField('Durum', choices=[
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('suspended', 'Askıda')
    ], validators=[DataRequired(message='Durum seçin')])
    notes = TextAreaField('Notlar', validators=[Optional()])


class SubnetForm(FlaskForm):
    """Form for creating/editing subnets."""
    network_address = StringField('Ağ Adresi', validators=[
        DataRequired(message='Ağ adresi gerekli')
    ])
    prefix_length = IntegerField('Prefix Uzunluğu', validators=[
        DataRequired(message='Prefix uzunluğu gerekli'),
        NumberRange(min=8, max=32, message='Prefix uzunluğu 8-32 arasında olmalı')
    ])
    status = SelectField('Durum', choices=[
        ('available', 'Kullanılabilir'),
        ('assigned', 'Atanmış'),
        ('reserved', 'Rezerve'),
        ('quarantined', 'Karantina')
    ], validators=[DataRequired(message='Durum seçin')])
    location = StringField('Lokasyon', validators=[
        Optional(),
        Length(max=100, message='Lokasyon çok uzun')
    ])
    vlan_id = IntegerField('VLAN ID', validators=[
        Optional(),
        NumberRange(min=1, max=4094, message='VLAN ID 1-4094 arasında olmalı')
    ])
    description = TextAreaField('Açıklama', validators=[Optional()])
    parent_subnet_id = SelectField('Üst Subnet', coerce=int, validators=[Optional()])
    auto_subdivide = BooleanField('Otomatik Alt Bölümlere Ayır')

    def __init__(self, *args, **kwargs):
        super(SubnetForm, self).__init__(*args, **kwargs)
        # Populate parent subnet choices
        self.parent_subnet_id.choices = [(0, '-- Yok --')] + [
            (s.id, s.cidr) for s in Subnet.query.order_by(Subnet.network_address).all()
        ]

    def validate_network_address(self, field):
        """Validate IP address format."""
        try:
            ipaddress.ip_address(field.data)
        except ValueError:
            raise ValidationError('Geçersiz IP adresi formatı')

    def validate(self):
        """Custom validation for subnet overlap."""
        if not super(SubnetForm, self).validate():
            return False

        # Check for network overlap
        try:
            new_network = ipaddress.ip_network(f"{self.network_address.data}/{self.prefix_length.data}")
        except ValueError:
            self.network_address.errors.append('Geçersiz ağ adresi')
            return False

        # Check overlap with existing subnets
        existing_subnets = Subnet.query.all()
        for subnet in existing_subnets:
            if hasattr(self, 'subnet_id') and subnet.id == self.subnet_id:
                continue  # Skip self in edit mode
            
            try:
                existing_network = ipaddress.ip_network(subnet.cidr)
                if new_network.overlaps(existing_network):
                    self.network_address.errors.append(
                        f'Bu ağ {subnet.cidr} ile çakışıyor'
                    )
                    return False
            except ValueError:
                continue

        return True


class AssignmentForm(FlaskForm):
    """Form for creating/editing assignments."""
    subnet_id = SelectField('Subnet', coerce=int, validators=[
        DataRequired(message='Subnet seçin')
    ])
    customer_id = SelectField('Müşteri', coerce=int, validators=[
        DataRequired(message='Müşteri seçin')
    ])
    start_date = DateField('Başlangıç Tarihi', validators=[
        DataRequired(message='Başlangıç tarihi gerekli')
    ], default=datetime.utcnow)
    end_date = DateField('Bitiş Tarihi', validators=[Optional()])
    price = DecimalField('Ücret', places=2, validators=[
        DataRequired(message='Ücret gerekli'),
        NumberRange(min=0, message='Ücret negatif olamaz')
    ])
    currency = SelectField('Para Birimi', choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRY', 'TRY')
    ], validators=[DataRequired(message='Para birimi seçin')])
    status = SelectField('Durum', choices=[
        ('active', 'Aktif'),
        ('expired', 'Süresi Dolmuş'),
        ('cancelled', 'İptal Edildi')
    ], validators=[DataRequired(message='Durum seçin')])
    auto_renew = BooleanField('Otomatik Yenile')
    notes = TextAreaField('Notlar', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        # Populate subnet choices (only available subnets)
        self.subnet_id.choices = [(0, '-- Subnet Seçin --')] + [
            (s.id, f"{s.cidr} - {s.location or 'Lokasyon yok'}")
            for s in Subnet.query.filter_by(status='available').order_by(Subnet.network_address).all()
        ]
        # Populate customer choices (only active customers)
        self.customer_id.choices = [(0, '-- Müşteri Seçin --')] + [
            (c.id, f"{c.name} ({c.type})")
            for c in Customer.query.filter_by(status='active').order_by(Customer.name).all()
        ]

    def validate_end_date(self, field):
        """Ensure end date is after start date."""
        if field.data and self.start_date.data:
            if field.data <= self.start_date.data:
                raise ValidationError('Bitiş tarihi başlangıç tarihinden sonra olmalı')


class SearchForm(FlaskForm):
    """Generic search form."""
    q = StringField('Ara', validators=[Optional()])
    status = SelectField('Durum', choices=[
        ('', 'Tümü'),
        ('active', 'Aktif'),
        ('inactive', 'Pasif')
    ], validators=[Optional()])


class ExchangeRateForm(FlaskForm):
    """Form for updating exchange rates."""
    from_currency = SelectField('Kaynak Para Birimi', choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRY', 'TRY')
    ], validators=[DataRequired()])
    to_currency = SelectField('Hedef Para Birimi', choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRY', 'TRY')
    ], validators=[DataRequired()])
    rate = DecimalField('Kur', places=6, validators=[
        DataRequired(message='Kur gerekli'),
        NumberRange(min=0.000001, message='Kur pozitif olmalı')
    ])

    def validate(self):
        """Ensure from and to currencies are different."""
        if not super(ExchangeRateForm, self).validate():
            return False
        
        if self.from_currency.data == self.to_currency.data:
            self.to_currency.errors.append('Kaynak ve hedef para birimleri farklı olmalı')
            return False
        
        return True
