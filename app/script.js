document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const imageFile = document.getElementById('image').files[0];
    const lowThreshold = parseFloat(document.getElementById('low_threshold').value);
    const upperThreshold = parseFloat(document.getElementById('upper_threshold').value);

    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('low_threshold', lowThreshold);
    formData.append('upper_threshold', upperThreshold);

    const response = await fetch('http://localhost:8000/generate_masks/', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        console.error('Error:', response.statusText);
        return;
    }

    const data = await response.json();
    displayMasks(data.high_frequency_mask, data.low_frequency_mask);
});

function displayMasks(highMask, lowMask) {
    const container = document.getElementById('masks-container');
    container.innerHTML = ''; // Clear previous results

    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container'; // Use flexbox for layout

    const highImg = document.createElement('img');
    highImg.src = `data:image/png;base64,${highMask}`;
    highImg.alt = 'High Frequency Mask';
    highImg.className = 'image-display'; // Use class for sizing

    const lowImg = document.createElement('img');
    lowImg.src = `data:image/png;base64,${lowMask}`;
    lowImg.alt = 'Low Frequency Mask';
    lowImg.className = 'image-display'; // Use class for sizing

    // Append images to the image container
    imageContainer.appendChild(highImg);
    imageContainer.appendChild(lowImg);

    // Append the image container to the main container
    container.appendChild(imageContainer);
}
