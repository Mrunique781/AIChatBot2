document.addEventListener('DOMContentLoaded', function() {
    const promptTextarea = document.getElementById('prompt');
    const generateBtn = document.getElementById('generateBtn');
    const formatBtns = document.querySelectorAll('.format-btn');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    
    let selectedFormat = null;

    // Format button click handlers
    formatBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            formatBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedFormat = btn.dataset.format;
            validateForm();
        });
    });

    // Prompt input handler
    promptTextarea.addEventListener('input', validateForm);

    // Form validation
    function validateForm() {
        const isValid = promptTextarea.value.trim() !== '' && selectedFormat !== null;
        generateBtn.disabled = !isValid;
    }

    // Generate button click handler
    generateBtn.addEventListener('click', async () => {
        const prompt = promptTextarea.value.trim();
        
        // Show loading state
        loadingDiv.classList.remove('d-none');
        errorDiv.classList.add('d-none');
        generateBtn.disabled = true;

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    format: selectedFormat
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate document');
            }

            // Get the blob from the response
            const blob = await response.blob();
            
            // Create a download link and trigger it
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `generated.${selectedFormat}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

        } catch (error) {
            errorDiv.textContent = 'Error generating document: ' + error.message;
            errorDiv.classList.remove('d-none');
        } finally {
            loadingDiv.classList.add('d-none');
            generateBtn.disabled = false;
        }
    });
});