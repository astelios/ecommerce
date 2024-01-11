$(document).ready(function() {
    $('#add-to-cart-button').click(function() {
        // AJAX request to fetch updated context data
        $.ajax({
            url: '/add_to_cart/',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                // Update only the relevant HTML elements
                $('#cart_badge').text(data.cart_badge_number);
            },
            error: function(error) {
                console.error('Error updating context:', error);
            }
        });
    });
});