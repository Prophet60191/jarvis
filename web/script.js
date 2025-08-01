// script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('myForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;

        // Validate form data
        if (name === '' || email === '') {
            alert('Please fill in all fields');
            return;
        }

        // Send form data to server (for demonstration purposes, we'll just log it)
        console.log(`Name: ${name}, Email: ${email}`);

        // Display submission result
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `Thank you for submitting the form!`;
    });
});
