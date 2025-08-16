"""Network utilities for CIDR calculations and subnet management."""
import ipaddress
from typing import List, Optional, Tuple

from app import db
from app.models import Subnet


def validate_cidr(cidr_str: str) -> bool:
    """Validate CIDR notation string."""
    try:
        ipaddress.ip_network(cidr_str, strict=False)
        return True
    except ValueError:
        return False


def validate_ip_address(ip_str: str) -> bool:
    """Validate IP address string."""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def parse_cidr(cidr_str: str) -> Optional[Tuple[str, int]]:
    """Parse CIDR string into network address and prefix length."""
    try:
        network = ipaddress.ip_network(cidr_str, strict=False)
        return str(network.network_address), network.prefixlen
    except ValueError:
        return None


def calculate_network_info(network_address: str, prefix_length: int) -> dict:
    """Calculate comprehensive network information."""
    try:
        network = ipaddress.ip_network(f"{network_address}/{prefix_length}")
        
        info = {
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address),
            'netmask': str(network.netmask),
            'hostmask': str(network.hostmask),
            'total_addresses': network.num_addresses,
            'usable_addresses': network.num_addresses - 2 if network.version == 4 and network.prefixlen < 31 else network.num_addresses,
            'first_host': str(network.network_address + 1) if network.version == 4 and network.prefixlen < 31 else str(network.network_address),
            'last_host': str(network.broadcast_address - 1) if network.version == 4 and network.prefixlen < 31 else str(network.broadcast_address),
            'version': network.version,
            'is_private': network.is_private,
            'is_global': network.is_global,
            'is_multicast': network.is_multicast,
            'is_reserved': network.is_reserved,
            'cidr': str(network)
        }
        
        return info
    except ValueError:
        return {}


def check_subnet_overlap(network_address: str, prefix_length: int, exclude_id: Optional[int] = None) -> List[dict]:
    """Check for subnet overlaps with existing subnets."""
    try:
        new_network = ipaddress.ip_network(f"{network_address}/{prefix_length}")
    except ValueError:
        return []
    
    overlapping_subnets = []
    query = Subnet.query
    if exclude_id:
        query = query.filter(Subnet.id != exclude_id)
    
    existing_subnets = query.all()
    
    for subnet in existing_subnets:
        try:
            existing_network = ipaddress.ip_network(subnet.cidr)
            if new_network.overlaps(existing_network):
                overlapping_subnets.append({
                    'id': subnet.id,
                    'cidr': subnet.cidr,
                    'status': subnet.status,
                    'location': subnet.location,
                    'description': subnet.description
                })
        except ValueError:
            continue
    
    return overlapping_subnets


def find_available_subnets(parent_cidr: str, desired_prefix: int, count: int = 1) -> List[str]:
    """Find available subnets within a parent network."""
    try:
        parent_network = ipaddress.ip_network(parent_cidr)
    except ValueError:
        return []
    
    if desired_prefix <= parent_network.prefixlen:
        return []
    
    available_subnets = []
    
    try:
        # Generate all possible subnets of desired size
        all_subnets = list(parent_network.subnets(new_prefix=desired_prefix))
        
        # Get existing subnets that might conflict
        existing_subnets = Subnet.query.all()
        existing_networks = []
        
        for subnet in existing_subnets:
            try:
                existing_networks.append(ipaddress.ip_network(subnet.cidr))
            except ValueError:
                continue
        
        # Find non-overlapping subnets
        for subnet in all_subnets:
            is_available = True
            
            for existing in existing_networks:
                if subnet.overlaps(existing):
                    is_available = False
                    break
            
            if is_available:
                available_subnets.append(str(subnet))
                if len(available_subnets) >= count:
                    break
        
    except ValueError:
        pass
    
    return available_subnets


def auto_subdivide_subnet(subnet_id: int, target_prefix: int = 24) -> List[dict]:
    """Automatically subdivide a subnet into smaller subnets."""
    subnet = Subnet.query.get(subnet_id)
    if not subnet:
        return []
    
    try:
        parent_network = ipaddress.ip_network(subnet.cidr)
    except ValueError:
        return []
    
    if target_prefix <= parent_network.prefixlen:
        return []
    
    created_subnets = []
    
    try:
        # Generate subnets
        child_subnets = list(parent_network.subnets(new_prefix=target_prefix))
        
        for i, child_network in enumerate(child_subnets):
            # Create new subnet record
            new_subnet = Subnet(
                network_address=str(child_network.network_address),
                prefix_length=child_network.prefixlen,
                parent_subnet_id=subnet.id,
                status='available',
                location=subnet.location,
                description=f'Auto-subdivided from {subnet.cidr} #{i+1}'
            )
            
            db.session.add(new_subnet)
            created_subnets.append(new_subnet.to_dict())
        
        # Mark parent as subdivided
        subnet.is_subdivided = True
        subnet.status = 'reserved'  # Parent is now reserved
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return []
    
    return created_subnets


def calculate_subnet_utilization(subnet_id: int) -> dict:
    """Calculate detailed utilization statistics for a subnet."""
    subnet = Subnet.query.get(subnet_id)
    if not subnet:
        return {}
    
    try:
        network = ipaddress.ip_network(subnet.cidr)
    except ValueError:
        return {}
    
    total_ips = network.num_addresses
    usable_ips = total_ips - 2 if network.version == 4 and network.prefixlen < 31 else total_ips
    
    # Count assigned IPs from child subnets
    assigned_ips = 0
    reserved_ips = 0
    
    for child in subnet.children:
        child_network = ipaddress.ip_network(child.cidr)
        child_ips = child_network.num_addresses
        
        if child.status == 'assigned':
            assigned_ips += child_ips
        elif child.status == 'reserved':
            reserved_ips += child_ips
    
    # If no children, check if the subnet itself is assigned
    if not subnet.children and subnet.status == 'assigned':
        assigned_ips = usable_ips
    
    available_ips = usable_ips - assigned_ips - reserved_ips
    utilization_percent = (assigned_ips / usable_ips * 100) if usable_ips > 0 else 0
    
    return {
        'total_ips': total_ips,
        'usable_ips': usable_ips,
        'assigned_ips': assigned_ips,
        'reserved_ips': reserved_ips,
        'available_ips': max(0, available_ips),
        'utilization_percent': round(utilization_percent, 2),
        'children_count': len(subnet.children),
        'is_fully_utilized': utilization_percent >= 100
    }


def suggest_subnet_size(required_hosts: int) -> int:
    """Suggest appropriate subnet prefix length for required host count."""
    # Add network and broadcast addresses for IPv4
    total_required = required_hosts + 2
    
    # Find the smallest subnet that can accommodate the hosts
    for prefix in range(30, 7, -1):  # /30 to /8
        network_size = 2 ** (32 - prefix)
        if network_size >= total_required:
            return prefix
    
    return 8  # Largest possible subnet /8


def get_subnet_hierarchy(subnet_id: int) -> dict:
    """Get the complete hierarchy for a subnet (parents and children)."""
    subnet = Subnet.query.get(subnet_id)
    if not subnet:
        return {}
    
    def build_hierarchy(s):
        return {
            'id': s.id,
            'cidr': s.cidr,
            'status': s.status,
            'location': s.location,
            'description': s.description,
            'utilization': s.utilization,
            'children': [build_hierarchy(child) for child in s.children]
        }
    
    # Find root parent
    root = subnet
    while root.parent:
        root = root.parent
    
    # Build complete hierarchy from root
    hierarchy = build_hierarchy(root)
    
    return hierarchy


def ip_in_subnet(ip_address: str, subnet_cidr: str) -> bool:
    """Check if an IP address belongs to a subnet."""
    try:
        ip = ipaddress.ip_address(ip_address)
        network = ipaddress.ip_network(subnet_cidr)
        return ip in network
    except ValueError:
        return False


def get_next_available_ip(subnet_cidr: str, exclude_ips: List[str] = None) -> Optional[str]:
    """Get the next available IP address in a subnet."""
    if exclude_ips is None:
        exclude_ips = []
    
    try:
        network = ipaddress.ip_network(subnet_cidr)
        
        # For /31 and /32, use all addresses
        if network.prefixlen >= 31:
            start_ip = network.network_address
            end_ip = network.broadcast_address
        else:
            # Skip network and broadcast addresses
            start_ip = network.network_address + 1
            end_ip = network.broadcast_address - 1
        
        current_ip = start_ip
        while current_ip <= end_ip:
            ip_str = str(current_ip)
            if ip_str not in exclude_ips:
                return ip_str
            current_ip += 1
            
    except ValueError:
        pass
    
    return None
