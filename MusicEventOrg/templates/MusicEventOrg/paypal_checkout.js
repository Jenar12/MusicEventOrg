async function initiatePaypalPayment(ticketId) {
    try {
        const response = await fetch('/api/initiate-paypal-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ ticket_id: ticketId })
        });
        const data = await response.json();
        if (data.error) {
            alert('Payment initiation failed: ' + data.error);
            return null;
        }
        return data.approval_url;
    } catch (error) {
        alert('Error initiating payment');
        console.error(error);
        return null;
    }
}

paypal.Buttons({
    createOrder: async function(data, actions) {
        const ticketId = prompt("Enter your ticket ID"); // Replace with actual ticket ID from your app
        if (!ticketId) return;
        const approvalUrl = await initiatePaypalPayment(ticketId);
        if (approvalUrl) {
            window.location.href = approvalUrl;
        }
    },
    onApprove: function(data, actions) {
        // Handled server-side in paypal_callback
    },
    onError: function(err) {
        console.error('PayPal error:', err);
        alert('An error occurred with PayPal');
    }
}).render('#paypal-button-container');