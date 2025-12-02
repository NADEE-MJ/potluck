// Main JavaScript for Potluck Organizer

// Copy to clipboard when clicking on code elements (shareable links)
document.addEventListener('DOMContentLoaded', function() {
    const codeElements = document.querySelectorAll('code');

    codeElements.forEach(function(codeElement) {
        codeElement.addEventListener('click', function() {
            const text = this.textContent;

            // Copy to clipboard
            navigator.clipboard.writeText(text).then(function() {
                // Show brief feedback
                const originalText = codeElement.textContent;
                codeElement.textContent = '✓ Copied!';
                codeElement.style.color = 'green';

                setTimeout(function() {
                    codeElement.textContent = originalText;
                    codeElement.style.color = '';
                }, 1500);
            }).catch(function(err) {
                console.error('Failed to copy:', err);
            });
        });
    });
});

// Auto-close details after form submission
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('details form');

    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            // The form will redirect, so we don't need to do anything special
        });
    });
});
