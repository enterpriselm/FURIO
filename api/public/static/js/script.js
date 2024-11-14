const apiUrl = 'https://furio.onrender.com' || 'http://localhost:8000';

document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    // Display loading spinner
    toggleSpinner(true);

    // Get the image file and threshold values from the form inputs
    const imageFile = document.getElementById('image').files[0];
    const lowThreshold = parseFloat(document.getElementById('low_threshold').value);
    const upperThreshold = parseFloat(document.getElementById('upper_threshold').value);

    // Create FormData to send to the server
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('low_threshold', lowThreshold);
    formData.append('upper_threshold', upperThreshold);

    try {
        // Send the request to the API
        const response = await fetch(`${apiUrl}/generate_masks/`, {
            method: 'POST',
            body: formData,
        });

        // Check if the response is OK
        if (!response.ok) {
            console.error('Error:', response.statusText);
            return;
        }

        const data = await response.json();
        displayMasks(data.image_array, data.high_frequency_mask, data.low_frequency_mask);
    } catch (error) {
        console.error('Error:', error);
    } finally {
        // Hide loading spinner
        toggleSpinner(false);
    }
});

function displayMasks(originalImg, highMask, lowMask) {
    const container = document.getElementById('masks-container');
    container.innerHTML = ''; // Clear previous results

    // Create a container div to hold the images
    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';

    // Create image elements and set their src as base64 data URLs
    const origImg = document.createElement('img');
    origImg.src = `data:image/png;base64,${originalImg}`;
    origImg.alt = 'Original Image';
    origImg.className = 'image-display';

    const highImg = document.createElement('img');
    highImg.src = `data:image/png;base64,${highMask}`;
    highImg.alt = 'High Frequency Mask';
    highImg.className = 'image-display';

    const lowImg = document.createElement('img');
    lowImg.src = `data:image/png;base64,${lowMask}`;
    lowImg.alt = 'Low Frequency Mask';
    lowImg.className = 'image-display';

    // Append images to container
    imageContainer.appendChild(origImg);
    imageContainer.appendChild(highImg);
    imageContainer.appendChild(lowImg);

    // Append the image container to the main container
    container.appendChild(imageContainer);
}

document.getElementById('cta-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Display loading spinner
    toggleSpinner(true);

    // Capture form data
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        company: document.getElementById('company').value,
        role: document.getElementById('role').value
    };

    fetch(`${apiUrl}/submit-form`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        alert('Thank you for reaching out!');
        document.getElementById('cta-form').reset();
    })
    .catch(error => {
        alert('There was an error submitting your form. Please try again.');
        console.error('Error:', error);
    })
    .finally(() => {
        // Hide loading spinner
        toggleSpinner(false);
    });
});

// Toggle spinner visibility
function toggleSpinner(show) {
    const spinner = document.getElementById('spinner');
    spinner.style.display = show ? 'block' : 'none';
}

// Create spinner element
document.addEventListener('DOMContentLoaded', () => {
    const spinner = document.createElement('div');
    spinner.id = 'spinner';
    spinner.style.display = 'none';
    spinner.innerHTML = `
        <div class="spinner-overlay">
            <div class="spinner"></div>
        </div>
    `;
    document.body.appendChild(spinner);
});