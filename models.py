from datetime import datetime, timedelta
from flask_login import UserMixin
import uuid

# In-memory data stores
users = []
customers = []
billings = []
ppp_connections = []

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = datetime.now()
    
    @classmethod
    def create(cls, username, email, password_hash, is_admin=False):
        user_id = len(users) + 1
        user = cls(user_id, username, email, password_hash, is_admin)
        users.append(user)
        return user
    
    @classmethod
    def get_by_id(cls, user_id):
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @classmethod
    def get_by_username(cls, username):
        for user in users:
            if user.username == username:
                return user
        return None
    
    @classmethod
    def get_by_email(cls, email):
        for user in users:
            if user.email == email:
                return user
        return None

class Customer:
    def __init__(self, id, name, email, phone, address, plan, username, password, notes=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.plan = plan  # Reference to plan name
        self.username = username
        self.password = password
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
    
    @classmethod
    def create(cls, name, email, phone, address, plan, username, password, notes=None):
        customer_id = len(customers) + 1
        customer = cls(customer_id, name, email, phone, address, plan, username, password, notes)
        customers.append(customer)
        # Create initial PPP connection
        PPPConnection.create(customer_id, "Offline")
        return customer
    
    @classmethod
    def get_by_id(cls, customer_id):
        for customer in customers:
            if customer.id == customer_id:
                return customer
        return None
    
    @classmethod
    def get_all(cls):
        return customers
    
    @classmethod
    def count(cls):
        return len(customers)
    
    def update(self, name=None, email=None, phone=None, address=None, plan=None, username=None, password=None, notes=None):
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        if plan is not None:
            self.plan = plan
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now()
        return self
    
    def delete(self):
        global customers
        customers = [c for c in customers if c.id != self.id]
        # Also delete related PPP connections and billings
        PPPConnection.delete_by_customer(self.id)
        Billing.delete_by_customer(self.id)
        return True

class Billing:
    def __init__(self, id, customer_id, amount, status, due_date, payment_date=None, payment_method=None, notes=None):
        self.id = id
        self.customer_id = customer_id
        self.amount = amount
        self.status = status  # Pending, Paid, Overdue
        self.due_date = due_date
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @classmethod
    def create(cls, customer_id, amount, status, due_date, payment_date=None, payment_method=None, notes=None):
        billing_id = str(uuid.uuid4())
        billing = cls(billing_id, customer_id, amount, status, due_date, payment_date, payment_method, notes)
        billings.append(billing)
        return billing
    
    @classmethod
    def get_by_id(cls, billing_id):
        for billing in billings:
            if billing.id == billing_id:
                return billing
        return None
    
    @classmethod
    def get_by_customer(cls, customer_id):
        return [b for b in billings if b.customer_id == customer_id]
    
    @classmethod
    def get_all(cls):
        return billings
    
    @classmethod
    def calculate_monthly_revenue(cls):
        current_month = datetime.now().month
        current_year = datetime.now().year
        total = 0
        for billing in billings:
            if billing.status == "Paid" and billing.payment_date:
                payment_date = billing.payment_date
                if payment_date.month == current_month and payment_date.year == current_year:
                    total += billing.amount
        return total
    
    @classmethod
    def count_pending_payments(cls):
        return sum(1 for b in billings if b.status == "Pending")
    
    @classmethod
    def delete_by_customer(cls, customer_id):
        global billings
        billings = [b for b in billings if b.customer_id != customer_id]
        return True
    
    def update(self, amount=None, status=None, due_date=None, payment_date=None, payment_method=None, notes=None):
        if amount is not None:
            self.amount = amount
        if status is not None:
            self.status = status
        if due_date is not None:
            self.due_date = due_date
        if payment_date is not None:
            self.payment_date = payment_date
        if payment_method is not None:
            self.payment_method = payment_method
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now()
        return self

class PPPConnection:
    def __init__(self, id, customer_id, status, ip_address=None, connected_since=None, last_disconnect=None):
        self.id = id
        self.customer_id = customer_id
        self.status = status  # Active or Offline
        self.ip_address = ip_address
        self.connected_since = connected_since
        self.last_disconnect = last_disconnect
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @classmethod
    def create(cls, customer_id, status, ip_address=None):
        connection_id = str(uuid.uuid4())
        connected_since = datetime.now() if status == "Active" else None
        connection = cls(connection_id, customer_id, status, ip_address, connected_since, None)
        ppp_connections.append(connection)
        return connection
    
    @classmethod
    def get_by_id(cls, connection_id):
        for connection in ppp_connections:
            if connection.id == connection_id:
                return connection
        return None
    
    @classmethod
    def get_by_customer(cls, customer_id):
        for connection in ppp_connections:
            if connection.customer_id == customer_id:
                return connection
        return None
    
    @classmethod
    def get_all(cls):
        return ppp_connections
    
    @classmethod
    def count_active(cls):
        return sum(1 for c in ppp_connections if c.status == "Active" or c.status == "Aktif")
    
    @classmethod
    def delete_by_customer(cls, customer_id):
        global ppp_connections
        ppp_connections = [c for c in ppp_connections if c.customer_id != customer_id]
        return True
    
    def update_status(self, status, ip_address=None):
        self.status = status
        if status == "Active":
            self.connected_since = datetime.now()
            self.ip_address = ip_address
        else:
            self.last_disconnect = datetime.now()
            self.ip_address = None
        self.updated_at = datetime.now()
        return self

# Initialize some default data for testing
def init_test_data():
    # Create admin user if none exists
    if len(users) == 0:
        from werkzeug.security import generate_password_hash
        User.create("admin", "admin@example.com", generate_password_hash("admin123"), is_admin=True)
        
        # Create some test customers, PPP connections, and billing records
        customer1 = Customer.create(
            "Budi Santoso", 
            "budi@example.com", 
            "081234567890", 
            "Jl. Sudirman No. 123, Jakarta", 
            "Paket Standar", 
            "budisantoso", 
            "password123", 
            "Pelanggan reguler"
        )
        
        customer2 = Customer.create(
            "Siti Rahma", 
            "siti@example.com", 
            "085678901234", 
            "Jl. Thamrin No. 45, Jakarta", 
            "Paket Premium", 
            "sitirahma", 
            "password456", 
            "Pelanggan premium"
        )
        
        # Create billing records (using IDR currency)
        Billing.create(
            customer1.id,
            250000,  # Rp 250.000 for Basic Plan
            "Lunas",  # Changed from "Paid" to Indonesian
            datetime.now() - timedelta(days=15),
            datetime.now() - timedelta(days=12),
            "Transfer Bank",
            "Paket Bulanan"
        )
        
        Billing.create(
            customer2.id,
            500000,  # Rp 500.000 for Premium Plan
            "Menunggu",  # Changed from "Pending" to Indonesian
            datetime.now() + timedelta(days=5),
            None,
            None,
            "Paket Bulanan"
        )
        
        # Update PPP connection status
        ppp1 = PPPConnection.get_by_customer(customer1.id)
        ppp1.update_status("Aktif", "192.168.1.100")  # Changed from "Active" to Indonesian

# Initialize test data
init_test_data()
