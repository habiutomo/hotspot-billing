/**
 * Main JavaScript file for Hotspot Billing System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Add current year to footer
    document.querySelector('footer p').innerHTML = document.querySelector('footer p').innerHTML.replace('{{ now.year }}', new Date().getFullYear());
    
    // Helper functions for use throughout the application
    window.utils = {
        // Format a currency value
        formatCurrency: function(amount) {
            return '$' + parseFloat(amount).toFixed(2);
        },
        
        // Format a date to locale string
        formatDate: function(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString();
        },
        
        // Format a datetime to locale string
        formatDateTime: function(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleString();
        },
        
        // Get appropriate badge class for connection status
        getConnectionStatusBadge: function(status) {
            switch(status) {
                case 'Active':
                    return 'badge bg-success';
                case 'Offline':
                    return 'badge bg-danger';
                default:
                    return 'badge bg-secondary';
            }
        },
        
        // Get appropriate badge class for billing status
        getBillingStatusBadge: function(status) {
            switch(status) {
                case 'Paid':
                    return 'badge bg-success';
                case 'Pending':
                    return 'badge bg-warning';
                case 'Overdue':
                    return 'badge bg-danger';
                default:
                    return 'badge bg-secondary';
            }
        },
        
        // Handle API errors
        handleApiError: function(error, elementId) {
            console.error('API Error:', error);
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading data. Please try again.
                    </div>
                `;
            }
        },
        
        // Show toast notification
        showToast: function(title, message, type = 'info') {
            // Create toast container if it doesn't exist
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                document.body.appendChild(toastContainer);
            }
            
            // Create toast element
            const toastId = 'toast-' + Date.now();
            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = 'toast';
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            // Set toast content based on type
            let bgClass = 'bg-light';
            let iconClass = 'fa-info-circle text-info';
            
            if (type === 'success') {
                iconClass = 'fa-check-circle text-success';
            } else if (type === 'warning') {
                iconClass = 'fa-exclamation-triangle text-warning';
            } else if (type === 'error') {
                iconClass = 'fa-exclamation-circle text-danger';
            }
            
            toast.innerHTML = `
                <div class="toast-header">
                    <i class="fas ${iconClass} me-2"></i>
                    <strong class="me-auto">${title}</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            
            // Add toast to container
            toastContainer.appendChild(toast);
            
            // Initialize and show toast
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 5000
            });
            bsToast.show();
            
            // Remove toast after it's hidden
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        },
        
        // Format a phone number
        formatPhoneNumber: function(phone) {
            if (!phone) return '';
            
            // Remove non-digit characters
            const digits = phone.replace(/\D/g, '');
            
            // Format based on length
            if (digits.length === 10) {
                return `(${digits.substring(0, 3)}) ${digits.substring(3, 6)}-${digits.substring(6)}`;
            } else if (digits.length === 11 && digits[0] === '1') {
                return `(${digits.substring(1, 4)}) ${digits.substring(4, 7)}-${digits.substring(7)}`;
            } else {
                return phone; // Return original if can't format
            }
        },
        
        // Calculate date difference in days
        dateDifference: function(startDate, endDate = new Date()) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            const diffTime = Math.abs(end - start);
            return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        }
    };
    
    // Add form validation styles
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});

/**
 * Confirm dialog helper
 * Usage: confirmAction('Are you sure?', 'This action cannot be undone', 'Yes, proceed').then(result => { if(result) { // do something } })
 */
function confirmAction(title, message, confirmText = 'OK', cancelText = 'Cancel') {
    return new Promise((resolve) => {
        // Create modal elements
        const modalId = 'confirm-modal-' + Date.now();
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = modalId;
        modalDiv.tabIndex = '-1';
        modalDiv.setAttribute('aria-hidden', 'true');
        
        modalDiv.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                        <button type="button" class="btn btn-primary" id="${modalId}-confirm">${confirmText}</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.appendChild(modalDiv);
        
        // Initialize modal
        const modal = new bootstrap.Modal(modalDiv);
        modal.show();
        
        // Handle confirm button
        document.getElementById(`${modalId}-confirm`).addEventListener('click', () => {
            modal.hide();
            resolve(true);
        });
        
        // Handle dismiss/cancel
        modalDiv.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modalDiv);
            resolve(false);
        });
    });
}

/**
 * Format date function
 * Converts a date object or string to YYYY-MM-DD format
 */
function formatDateYYYYMMDD(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}

/**
 * Handle API errors with consistent messaging
 */
function handleApiError(error, containerId, message = 'An error occurred while fetching data.') {
    console.error('API Error:', error);
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}
