// Simple, reliable comma formatting for integer fields
(function() {
    'use strict';
    
    console.log('Django Comma Integer Field script loaded');
    
    function addCommas(num) {
        // Convert to string and remove any existing commas
        let str = num.toString().replace(/,/g, '');
        
        // Handle empty or invalid input
        if (!str || str === '' || str === '-') return str;
        
        // Handle negative numbers
        let isNegative = str.startsWith('-');
        if (isNegative) {
            str = str.substring(1);
        }
        
        // Add commas every 3 digits from the right
        str = str.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        
        // Add back negative sign if needed
        return isNegative ? '-' + str : str;
    }
    
    function removeCommas(str) {
        return str.replace(/,/g, '');
    }
    
    function formatField(field) {
        const currentValue = field.value;
        const cursorPos = field.selectionStart;
        const formattedValue = addCommas(currentValue);
        
        console.log('Formatting:', currentValue, '->', formattedValue);
        
        field.value = formattedValue;
        
        // Adjust cursor position
        const diff = formattedValue.length - currentValue.length;
        field.setSelectionRange(cursorPos + diff, cursorPos + diff);
    }
    
    function setupField(field) {
        console.log('Setting up field:', field);
        
        // Format initial value
        if (field.value) {
            field.value = addCommas(field.value);
        }
        
        // Add event listeners
        field.addEventListener('input', function(e) {
            console.log('Input event triggered');
            formatField(this);
        });
        
        field.addEventListener('keypress', function(e) {
            // Only allow numbers, minus, backspace, delete, etc.
            const char = String.fromCharCode(e.which);
            if (!/[\d-]/.test(char) && e.which !== 8 && e.which !== 0) {
                e.preventDefault();
            }
        });
        
        // Remove commas before form submission
        const form = field.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                field.value = removeCommas(field.value);
            });
        }
    }
    
    function initializeFields() {
        console.log('Initializing comma integer fields');
        
        // Find all input fields that should have comma formatting
        const selectors = [
            '.comma-integer-field',
            'input[name*="aa"]',  // Fallback for field name patterns
            'input[type="text"][class*="comma-integer"]'
        ];
        
        selectors.forEach(selector => {
            const fields = document.querySelectorAll(selector);
            console.log(`Found ${fields.length} fields with selector: ${selector}`);
            
            fields.forEach(field => {
                // Avoid double-initialization
                if (!field.hasAttribute('data-comma-initialized')) {
                    field.setAttribute('data-comma-initialized', 'true');
                    setupField(field);
                }
            });
        });
    }
    
    // Try multiple initialization strategies
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFields);
    } else {
        initializeFields();
    }
    
    // Also try after a short delay
    setTimeout(initializeFields, 500);
    setTimeout(initializeFields, 1000);
    
    // For Django admin, also try when jQuery is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(function() {
            console.log('Django jQuery ready');
            initializeFields();
        });
    }
    
    // Fallback for regular jQuery
    if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(function() {
            console.log('Regular jQuery ready');
            initializeFields();
        });
    }
    
})();
