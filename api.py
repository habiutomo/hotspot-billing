from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Customer, Billing, PPPConnection
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Customer API endpoints
@api_bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    customers_list = Customer.get_all()
    result = []
    
    for customer in customers_list:
        connection = PPPConnection.get_by_customer(customer.id)
        billings = Billing.get_by_customer(customer.id)
        
        # Find latest billing
        latest_billing = None
        for billing in billings:
            if latest_billing is None or billing.due_date > latest_billing.due_date:
                latest_billing = billing
        
        result.append({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'plan': customer.plan,
            'username': customer.username,
            'status': 'Active' if customer.is_active else 'Inactive',
            'connection_status': connection.status if connection else 'Unknown',
            'latest_bill_status': latest_billing.status if latest_billing else 'No bills',
            'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return jsonify(result)

@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@login_required
def get_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    connection = PPPConnection.get_by_customer(customer.id)
    billings = Billing.get_by_customer(customer.id)
    
    # Format billing records
    billing_history = []
    for billing in billings:
        billing_history.append({
            'id': billing.id,
            'amount': billing.amount,
            'status': billing.status,
            'due_date': billing.due_date.strftime('%Y-%m-%d'),
            'payment_date': billing.payment_date.strftime('%Y-%m-%d') if billing.payment_date else None,
            'payment_method': billing.payment_method,
            'notes': billing.notes
        })
    
    result = {
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address,
        'plan': customer.plan,
        'username': customer.username,
        'notes': customer.notes,
        'status': 'Active' if customer.is_active else 'Inactive',
        'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'connection': {
            'status': connection.status if connection else 'Unknown',
            'ip_address': connection.ip_address if connection and connection.ip_address else None,
            'connected_since': connection.connected_since.strftime('%Y-%m-%d %H:%M:%S') if connection and connection.connected_since else None,
            'last_disconnect': connection.last_disconnect.strftime('%Y-%m-%d %H:%M:%S') if connection and connection.last_disconnect else None
        },
        'billing_history': billing_history
    }
    
    return jsonify(result)

@api_bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    data = request.json
    
    required_fields = ['name', 'email', 'phone', 'address', 'plan', 'username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create customer
    customer = Customer.create(
        data['name'],
        data['email'],
        data['phone'],
        data['address'],
        data['plan'],
        data['username'],
        data['password'],
        data.get('notes')
    )
    
    return jsonify({
        'id': customer.id,
        'message': 'Customer created successfully'
    }), 201

@api_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.json
    
    # Update customer
    customer.update(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        plan=data.get('plan'),
        username=data.get('username'),
        password=data.get('password'),
        notes=data.get('notes')
    )
    
    return jsonify({
        'message': 'Customer updated successfully'
    })

@api_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    customer = Customer.get_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer.delete()
    
    return jsonify({
        'message': 'Customer deleted successfully'
    })

# PPP Connection API endpoints
@api_bp.route('/connections', methods=['GET'])
@login_required
def get_connections():
    connections = PPPConnection.get_all()
    result = []
    
    for connection in connections:
        customer = Customer.get_by_id(connection.customer_id)
        if customer:
            result.append({
                'id': connection.id,
                'customer_id': connection.customer_id,
                'customer_name': customer.name,
                'username': customer.username,
                'status': connection.status,
                'ip_address': connection.ip_address,
                'connected_since': connection.connected_since.strftime('%Y-%m-%d %H:%M:%S') if connection.connected_since else None,
                'last_disconnect': connection.last_disconnect.strftime('%Y-%m-%d %H:%M:%S') if connection.last_disconnect else None
            })
    
    return jsonify(result)

@api_bp.route('/connections/<int:customer_id>', methods=['PUT'])
@login_required
def update_connection(customer_id):
    connection = PPPConnection.get_by_customer(customer_id)
    if not connection:
        return jsonify({'error': 'Connection not found'}), 404
    
    data = request.json
    
    if 'status' not in data:
        return jsonify({'error': 'Missing required field: status'}), 400
    
    if data['status'] not in ['Active', 'Offline']:
        return jsonify({'error': 'Status must be either Active or Offline'}), 400
    
    # Update connection status
    connection.update_status(data['status'], data.get('ip_address'))
    
    return jsonify({
        'message': f'Connection status updated to {data["status"]}'
    })

# Billing API endpoints
@api_bp.route('/billings', methods=['GET'])
@login_required
def get_billings():
    status_filter = request.args.get('status')
    billings_list = Billing.get_all()
    
    # Apply filter if provided
    if status_filter:
        billings_list = [b for b in billings_list if b.status.lower() == status_filter.lower()]
    
    result = []
    for billing in billings_list:
        customer = Customer.get_by_id(billing.customer_id)
        if customer:
            result.append({
                'id': billing.id,
                'customer_id': billing.customer_id,
                'customer_name': customer.name,
                'amount': billing.amount,
                'status': billing.status,
                'due_date': billing.due_date.strftime('%Y-%m-%d'),
                'payment_date': billing.payment_date.strftime('%Y-%m-%d') if billing.payment_date else None,
                'payment_method': billing.payment_method,
                'notes': billing.notes
            })
    
    return jsonify(result)

@api_bp.route('/billings', methods=['POST'])
@login_required
def create_billing():
    data = request.json
    
    required_fields = ['customer_id', 'amount', 'status', 'due_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if customer exists
    customer = Customer.get_by_id(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Parse date strings
    try:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d') if data.get('payment_date') else None
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Create billing
    billing = Billing.create(
        data['customer_id'],
        float(data['amount']),
        data['status'],
        due_date,
        payment_date,
        data.get('payment_method'),
        data.get('notes')
    )
    
    return jsonify({
        'id': billing.id,
        'message': 'Billing record created successfully'
    }), 201

@api_bp.route('/billings/<string:billing_id>', methods=['PUT'])
@login_required
def update_billing(billing_id):
    billing = Billing.get_by_id(billing_id)
    if not billing:
        return jsonify({'error': 'Billing record not found'}), 404
    
    data = request.json
    
    # Parse date strings if provided
    due_date = None
    if 'due_date' in data:
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
    
    payment_date = None
    if 'payment_date' in data:
        try:
            payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d') if data['payment_date'] else None
        except ValueError:
            return jsonify({'error': 'Invalid payment_date format. Use YYYY-MM-DD'}), 400
    
    # Update billing
    amount = float(data['amount']) if 'amount' in data else None
    billing.update(
        amount=amount,
        status=data.get('status'),
        due_date=due_date,
        payment_date=payment_date,
        payment_method=data.get('payment_method'),
        notes=data.get('notes')
    )
    
    return jsonify({
        'message': 'Billing record updated successfully'
    })

# Reports API endpoints
@api_bp.route('/reports/revenue', methods=['GET'])
@login_required
def revenue_report():
    # Get query parameters for date range
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            # Default to beginning of current month
            today = datetime.now()
            start_date = datetime(today.year, today.month, 1)
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to today
            end_date = datetime.now()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get paid billings within the date range
    filtered_billings = [b for b in Billing.get_all()
                        if b.status == "Paid" and b.payment_date 
                        and start_date <= b.payment_date <= end_date]
    
    # Calculate total revenue
    total_revenue = sum(b.amount for b in filtered_billings)
    
    # Group by payment method
    payment_methods = {}
    for billing in filtered_billings:
        method = billing.payment_method or "Unknown"
        if method not in payment_methods:
            payment_methods[method] = 0
        payment_methods[method] += billing.amount
    
    return jsonify({
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_revenue': total_revenue,
        'payment_methods': payment_methods,
        'transaction_count': len(filtered_billings)
    })

@api_bp.route('/reports/connections', methods=['GET'])
@login_required
def connection_report():
    connections = PPPConnection.get_all()
    
    active_count = sum(1 for c in connections if c.status == "Active")
    offline_count = sum(1 for c in connections if c.status == "Offline")
    
    # Get active connections with details
    active_connections = []
    for connection in connections:
        if connection.status == "Active":
            customer = Customer.get_by_id(connection.customer_id)
            if customer:
                active_connections.append({
                    'customer_name': customer.name,
                    'username': customer.username,
                    'ip_address': connection.ip_address,
                    'connected_since': connection.connected_since.strftime('%Y-%m-%d %H:%M:%S') if connection.connected_since else None
                })
    
    return jsonify({
        'total_customers': len(connections),
        'active_count': active_count,
        'offline_count': offline_count,
        'active_percentage': (active_count / len(connections) * 100) if connections else 0,
        'active_connections': active_connections
    })

@api_bp.route('/reports/billing_status', methods=['GET'])
@login_required
def billing_status_report():
    billings = Billing.get_all()
    
    # Count by status
    status_counts = {
        'Paid': 0,
        'Pending': 0,
        'Overdue': 0
    }
    
    total_amount = 0
    pending_amount = 0
    overdue_amount = 0
    
    for billing in billings:
        if billing.status in status_counts:
            status_counts[billing.status] += 1
        
        total_amount += billing.amount
        
        if billing.status == 'Pending':
            pending_amount += billing.amount
        elif billing.status == 'Overdue':
            overdue_amount += billing.amount
    
    return jsonify({
        'status_counts': status_counts,
        'total_amount': total_amount,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'collection_rate': ((total_amount - pending_amount - overdue_amount) / total_amount * 100) if total_amount > 0 else 0
    })
