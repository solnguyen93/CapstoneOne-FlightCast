<script>
const form = document.getElementById('flight-search-form');
const resultsDiv = document.getElementById('flight-results');

form.addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent the form from submitting and refreshing the page

    // Get user input values
    const departureCity = document.getElementById('departure-city').value;
    const arrivalCity = document.getElementById('arrival-city').value;
    const departureDate = document.getElementById('departure-date').value;

    // Simulate an API request (replace with your actual API endpoint)
    fetch('/api/search-flights', {
        method: 'POST',
        body: JSON.stringify({ departureCity, arrivalCity, departureDate }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Display flight search results in the resultsDiv
        resultsDiv.innerHTML = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        console.error('Error:', error);
        resultsDiv.innerHTML = 'An error occurred while fetching flight data.';
    });
});
</script>