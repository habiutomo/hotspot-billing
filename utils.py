from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

def format_currency(amount):
    """Format a number as Indonesian Rupiah (IDR) with no decimal places
    and thousand separators with dot, e.g. Rp 1.000.000"""
    # Format with thousand separators using dot (.) and no decimal places
    formatted_amount = f"{int(amount):,}".replace(',', '.')
    return f"Rp {formatted_amount}"

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
    if status == "Active" or status == "Aktif":
        return "badge bg-success"
    elif status == "Offline" or status == "Tidak Aktif":
        return "badge bg-danger"
    else:
        return "badge bg-secondary"

def get_billing_status_badge(status):
    """Get the appropriate Bootstrap badge class for a billing status"""
    if status == "Paid" or status == "Lunas":
        return "badge bg-success"
    elif status == "Pending" or status == "Menunggu":
        return "badge bg-warning"
    elif status == "Overdue" or status == "Terlambat":
        return "badge bg-danger"
    else:
        return "badge bg-secondary"

def format_phone_number(phone):
    """Format an Indonesian phone number for display"""
    if not phone:
        return ""
    
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length and prefix
    if len(digits) >= 10:
        # Check if it starts with country code (62)
        if digits.startswith('62'):
            # Convert 62 prefix to 0
            digits = '0' + digits[2:]
            
        # Handle common Indonesian mobile formats (typically start with 08)
        if digits.startswith('08'):
            # Format as 08xx-xxxx-xxxx
            if len(digits) == 11:
                return f"{digits[0:4]}-{digits[4:8]}-{digits[8:]}"
            elif len(digits) == 12:
                return f"{digits[0:4]}-{digits[4:8]}-{digits[8:]}"
            else:
                return f"{digits[0:4]}-{digits[4:8]}-{digits[8:12]}"
        
    # If we can't specifically format it, just group in 4s
    return '-'.join([digits[i:i+4] for i in range(0, len(digits), 4)])
