// Get the button and counter element
var incrementButton = document.getElementById('add-to-cart-button');
var counterElement = document.getElementById('cart-badge');

// Initialize counter variable
var counter = 0;

// Attach click event listener to the button
incrementButton.addEventListener('click', function() {
    // Increment the counter
    counter++;

    // Update the counter element text
    counterElement.textContent = counter;
});