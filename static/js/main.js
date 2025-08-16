// IPAM Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Copy to clipboard functionality
    initializeCopyToClipboard();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Copy to Clipboard
function initializeCopyToClipboard() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy || this.getAttribute('data-copy');
            
            if (textToCopy) {
                copyToClipboard(textToCopy, this);
            }
        });
    });
}

function copyToClipboard(text, button = null) {
    // Try using the modern Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(button);
        }).catch(function() {
            fallbackCopyToClipboard(text, button);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyToClipboard(text, button);
    }
}

function fallbackCopyToClipboard(text, button = null) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(button);
        } else {
            showCopyError(button);
        }
    } catch (err) {
        showCopyError(button);
    } finally {
        document.body.removeChild(textArea);
    }
}

function showCopySuccess(button = null) {
    if (button) {
        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        button.innerHTML = '<i class="fas fa-check"></i> Kopyalandı!';
        button.className = button.className.replace('btn-outline-secondary', 'btn-success').replace('btn-secondary', 'btn-success');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.className = originalClass;
        }, 2000);
    }
    
    showToast('Kopyalandı!', 'Metin başarıyla panoya kopyalandı.', 'success');
}

function showCopyError(button = null) {
    if (button) {
        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        button.innerHTML = '<i class="fas fa-times"></i> Hata!';
        button.className = button.className.replace('btn-outline-secondary', 'btn-danger').replace('btn-secondary', 'btn-danger');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.className = originalClass;
        }, 2000);
    }
    
    showToast('Hata!', 'Metin kopyalanamadı.', 'error');
}

// Toast Notifications
function showToast(title, message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    const toastId = 'toast_' + Date.now();
    
    const toastHtml = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" id="${toastId}">
            <div class="toast-header">
                <i class="fas fa-${getToastIcon(type)} text-${getToastColor(type)} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    
    return container;
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || icons.info;
}

function getToastColor(type) {
    const colors = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colors[type] || colors.info;
}

// Form Validations
function initializeFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // CIDR validation
    const cidrInputs = document.querySelectorAll('input[data-validate="cidr"]');
    cidrInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateCIDR(this);
        });
    });
    
    // IP address validation
    const ipInputs = document.querySelectorAll('input[data-validate="ip"]');
    ipInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateIP(this);
        });
    });
}

function validateCIDR(input) {
    const cidrRegex = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$/;
    
    if (input.value && !cidrRegex.test(input.value)) {
        input.setCustomValidity('Geçerli bir CIDR formatı girin (örn: 192.168.1.0/24)');
    } else {
        input.setCustomValidity('');
    }
}

function validateIP(input) {
    const ipRegex = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/;
    
    if (input.value && !ipRegex.test(input.value)) {
        input.setCustomValidity('Geçerli bir IP adresi girin (örn: 192.168.1.1)');
    } else {
        input.setCustomValidity('');
    }
}

// Charts
function initializeCharts() {
    // Dashboard utilization chart
    const utilizationChart = document.getElementById('utilizationChart');
    if (utilizationChart) {
        createUtilizationChart(utilizationChart);
    }
    
    // Revenue chart
    const revenueChart = document.getElementById('revenueChart');
    if (revenueChart) {
        createRevenueChart(revenueChart);
    }
}

function createUtilizationChart(ctx) {
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Kullanılan', 'Boş'],
            datasets: [{
                data: [30, 70],
                backgroundColor: ['#0d6efd', '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createRevenueChart(ctx) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
            datasets: [{
                label: 'Gelir (TRY)',
                data: [1200, 1900, 1500, 2200, 1800, 2500],
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₺' + value.toLocaleString('tr-TR');
                        }
                    }
                }
            }
        }
    });
}

// Utility Functions
function formatCurrency(amount, currency = 'TRY') {
    const symbols = {
        'TRY': '₺',
        'USD': '$',
        'EUR': '€'
    };
    
    return symbols[currency] + amount.toLocaleString('tr-TR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatIPCount(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
    } else {
        return count.toString();
    }
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Loading states
function showLoading(element) {
    if (element) {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yükleniyor...';
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element && element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
        delete element.dataset.originalContent;
    }
}

// AJAX helpers
function makeRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const config = Object.assign({}, defaults, options);
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            showToast('Hata!', 'İstek başarısız oldu: ' + error.message, 'error');
            throw error;
        });
}

// Export functions for use in other scripts
window.IPAM = {
    copyToClipboard,
    showToast,
    showLoading,
    hideLoading,
    makeRequest,
    formatCurrency,
    formatIPCount,
    debounce
};
