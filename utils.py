from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

def format_currency(amount):
    """Format a number as currency with 2 decimal places"""
    return f"${amount:.2f}"

def calculate_date_difference(start_date, end_date=None):
    """Calculate the difference between two dates in days"""
    if end_date is None:
        end_date = datetime.now()
    
    difference = end_date - start_date
    return difference.days

def format_datetime(dt):
    """Format a datetime object as a string"""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_date(dt):
    """Format a datetime object as a date string"""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d")

def get_connection_status_badge(status):
    """Get the appropriate Bootstrap badge class for a connection status"""
    if status == "Active":
        return "badge bg-success"
    elif status == "Offline":
        return "badge bg-danger"
    else:
        return "badge bg-secondary"

def get_billing_status_badge(status):
    """Get the appropriate Bootstrap badge class for a billing status"""
    if status == "Paid":
        return "badge bg-success"
    elif status == "Pending":
        return "badge bg-warning"
    elif status == "Overdue":
        return "badge bg-danger"
    else:
        return "badge bg-secondary"

def format_phone_number(phone):
    """Format a phone number for display"""
    if not phone:
        return ""
    
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if we can't format it
