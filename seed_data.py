"""Seed database with initial data for development and testing."""
from datetime import datetime, date
from decimal import Decimal

from app import db
from app.models import User, Customer, Subnet, Assignment, ExchangeRate


def seed_database():
    """Seed database with sample data."""
    
    # Create users
    print("Creating users...")
    
    # Admin user
    admin = User(
        username='admin',
        email='admin@ipam.local',
        is_admin=True,
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Manager user  
    manager = User(
        username='manager',
        email='manager@ipam.local',
        is_admin=False,
        is_active=True
    )
    manager.set_password('manager123')
    db.session.add(manager)
    
    # Operator user
    operator = User(
        username='operator',
        email='operator@ipam.local',
        is_admin=False,
        is_active=True
    )
    operator.set_password('operator123')
    db.session.add(operator)
    
    try:
        db.session.commit()
        print("✓ Users created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating users: {e}")
        return
    
    # Create customers
    print("Creating customers...")
    
    customers_data = [
        {
            'name': 'Acme Corporation',
            'type': 'company',
            'email': 'contact@acme.com',
            'phone': '+90 212 555 0101',
            'address': 'Maslak Mahallesi, İTÜ Ayazağa Kampüsü, Sarıyer/İstanbul',
            'status': 'active',
            'notes': 'Kurumsal müşteri - öncelikli destek'
        },
        {
            'name': 'TechStart Ltd.',
            'type': 'company',
            'email': 'info@techstart.com.tr',
            'phone': '+90 216 555 0202',
            'address': 'Kadıköy, İstanbul',
            'status': 'active',
            'notes': 'Startup şirketi'
        },
        {
            'name': 'Ahmet Yılmaz',
            'type': 'individual',
            'email': 'ahmet.yilmaz@example.com',
            'phone': '+90 532 555 0303',
            'address': 'Beyoğlu, İstanbul',
            'status': 'active',
            'notes': 'Bireysel geliştiriciler'
        },
        {
            'name': 'DataCorp Solutions',
            'type': 'company',
            'email': 'admin@datacorp.com.tr',
            'phone': '+90 312 555 0404',
            'address': 'Çankaya, Ankara',
            'status': 'active',
            'notes': 'Veri merkezi hizmetleri'
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        customers.append(customer)
        db.session.add(customer)
    
    try:
        db.session.commit()
        print("✓ Customers created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating customers: {e}")
        return
    
    # Create subnets
    print("Creating subnets...")
    
    subnets_data = [
        {
            'network_address': '192.168.1.0',
            'prefix_length': 24,
            'status': 'available',
            'location': 'İstanbul DC1',
            'vlan_id': 100,
            'description': 'Ana subnet - İstanbul veri merkezi'
        },
        {
            'network_address': '192.168.2.0',
            'prefix_length': 24,
            'status': 'assigned',
            'location': 'İstanbul DC1',
            'vlan_id': 101,
            'description': 'Web sunucuları'
        },
        {
            'network_address': '10.0.1.0',
            'prefix_length': 24,
            'status': 'available',
            'location': 'Ankara DC1',
            'vlan_id': 200,
            'description': 'Ankara veri merkezi - genel amaçlı'
        },
        {
            'network_address': '172.16.10.0',
            'prefix_length': 24,
            'status': 'reserved',
            'location': 'İstanbul DC2',
            'vlan_id': 300,
            'description': 'Gelecekteki genişleme için rezerve'
        },
        {
            'network_address': '192.168.100.0',
            'prefix_length': 26,
            'status': 'assigned',
            'location': 'İstanbul DC1',
            'vlan_id': 150,
            'description': 'Test ortamı'
        }
    ]
    
    subnets = []
    for subnet_data in subnets_data:
        subnet = Subnet(**subnet_data)
        subnets.append(subnet)
        db.session.add(subnet)
    
    try:
        db.session.commit()
        print("✓ Subnets created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating subnets: {e}")
        return
    
    # Create assignments
    print("Creating assignments...")
    
    assignments_data = [
        {
            'subnet_id': subnets[1].id,  # 192.168.2.0/24 (assigned)
            'customer_id': customers[0].id,  # Acme Corporation
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'price': Decimal('1500.00'),
            'currency': 'TRY',
            'status': 'active',
            'notes': 'Web hosting hizmetleri için',
            'auto_renew': True
        },
        {
            'subnet_id': subnets[4].id,  # 192.168.100.0/26 (assigned)
            'customer_id': customers[1].id,  # TechStart Ltd.
            'start_date': date(2024, 6, 1),
            'end_date': date(2025, 5, 31),
            'price': Decimal('800.00'),
            'currency': 'TRY',
            'status': 'active',
            'notes': 'Test ve geliştirme ortamı',
            'auto_renew': False
        }
    ]
    
    for assignment_data in assignments_data:
        assignment = Assignment(**assignment_data)
        db.session.add(assignment)
    
    try:
        db.session.commit()
        print("✓ Assignments created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating assignments: {e}")
        return
    
    # Create exchange rates
    print("Creating exchange rates...")
    
    exchange_rates_data = [
        # USD base rates
        {'from_currency': 'USD', 'to_currency': 'TRY', 'rate': Decimal('31.5000')},
        {'from_currency': 'USD', 'to_currency': 'EUR', 'rate': Decimal('0.9200')},
        
        # EUR base rates
        {'from_currency': 'EUR', 'to_currency': 'USD', 'rate': Decimal('1.0870')},
        {'from_currency': 'EUR', 'to_currency': 'TRY', 'rate': Decimal('34.2000')},
        
        # TRY base rates
        {'from_currency': 'TRY', 'to_currency': 'USD', 'rate': Decimal('0.0317')},
        {'from_currency': 'TRY', 'to_currency': 'EUR', 'rate': Decimal('0.0292')},
    ]
    
    for rate_data in exchange_rates_data:
        rate = ExchangeRate(**rate_data)
        db.session.add(rate)
    
    try:
        db.session.commit()
        print("✓ Exchange rates created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating exchange rates: {e}")
        return
    
    print("\n🎉 Database seeded successfully!")
    print("\nDefault login credentials:")
    print("Admin: admin / admin123")
    print("Manager: manager / manager123")
    print("Operator: operator / operator123")


if __name__ == '__main__':
    seed_database()
