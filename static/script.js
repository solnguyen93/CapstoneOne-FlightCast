console.log('JavaScript is running!'); // ******************** TEST ******************** REMOVE AFTER

document.addEventListener("DOMContentLoaded", async function () {

    const token = await getToken();

// Get token from session or fetch 
    async function getToken() {
        let token = sessionStorage.getItem('token');
        if (!token) {
            token = await fetchToken();
        }
        return token;
    }

// Fetch token from Python/Server
    async function fetchToken() {
        try {
            const response = await fetch('/token');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            sessionStorage.setItem('token', data.token);
            return data.token;
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }

// Auto complete user's input on From and To 
    // Function to show city suggestions to autocomplete
    function showCitySuggestions(suggestionsElementId, suggestions) {
        const suggestionsElement = document.getElementById(suggestionsElementId);
        suggestionsElement.innerHTML = suggestions.map(suggestion => {
            return `<div class="suggestion-item" onclick="selectSuggestion('${suggestion.name}', '${suggestionsElementId}')">${suggestion.name}</div>`;
        }).join('');
    }
  
    // Function to handle suggestion selection
    function selectSuggestion(selectedName, suggestionsElementId) {
        const inputId = suggestionsElementId.replace('-suggestions', '');
        const inputElement = document.getElementById(inputId);
        inputElement.value = selectedName;
        document.getElementById(suggestionsElementId).innerHTML = '';
    }
  
    // Function to fetch city suggestions from the API
    async function fetchCitySuggestions(userInput, suggestionsElementId) {
        if (userInput.length >= 3) {
            const baseUrl = "https://test.api.amadeus.com/v1/reference-data/locations";
            const url = `${baseUrl}?subType=CITY,AIRPORT&keyword=${userInput}`;
            try {
                const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
                });
                if (!response.ok) {
                throw new Error('Failed to fetch locations');
                }
                const data = await response.json();
                showCitySuggestions(suggestionsElementId, data.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    }
    
    const departureCityInput = document.getElementById('departure-city');
    if (departureCityInput) {
        departureCityInput.addEventListener('input', function() {
        fetchCitySuggestions(this.value, 'departure-city-suggestions');
        });
    }

    const arrivalCityInput = document.getElementById('arrival-city');
    if (arrivalCityInput) {
        arrivalCityInput.addEventListener('input', function() {
        fetchCitySuggestions(this.value, 'arrival-city-suggestions');
        });
    }
      
  
    
  











// Clear session when log out
    function logoutUser() {
        sessionStorage.clear();
    }
    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutUser);
    }

// Client side validation on search form data
    const searchForm = document.querySelector("#flight-search-form");  
    if (searchForm) {
        searchForm.addEventListener("submit", async function (event) {
            // Helper function to check if a string contains only alphabetic characters
            function isValidString(str) {
                return /^[a-zA-Z]+$/.test(str);
            }
            // Helper function to check if date is valid
            function isValidDate(date) {
                const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
                return dateRegex.test(date);
            }
            const departureCity = document.getElementById("departure-city").value;
            const arrivalCity = document.getElementById("arrival-city").value;
            const departDate = document.getElementById("depart-date").value;
            const returnDate = document.getElementById("return-date").value;
            const passengers = document.getElementById("passengers").value;
            if (!isValidString(departureCity)) {
                showFlashMessage('Departure city must contain only alphabetic characters.', 'error');
                event.preventDefault();
                return;
            }  
            if (!isValidString(arrivalCity)) {
                showFlashMessage('Arrival city must contain only alphabetic characters.', 'error');
                event.preventDefault();
                return;
            } 
            if (!isValidDate(departDate)) {
                showFlashMessage('Depart date must be in the format mm/dd/yyyy.', 'error');
                event.preventDefault();
                return;
            } 
            if (!isValidDate(returnDate)) {
                showFlashMessage('Return date must be in the format mm/dd/yyyy.', 'error');
                event.preventDefault();
                return;
            } 
            // Convert date strings to Date objects in the user's local time zone
            function parseDateString(dateString) {
                const [year, month, day] = dateString.split('-').map(Number);
                return new Date(year, month - 1, day);
            }
            const departDateObj = parseDateString(departDate);
            const returnDateObj = parseDateString(returnDate);
            // Check if depart date is today or later
            let today = new Date();
            today.setHours(0, 0, 0, 0); // Set time to midnight for comparison
            if (departDateObj <= today) {
                showFlashMessage('Depart date must be tomorrow or later.', 'error');
                event.preventDefault();
                return;
            }
            // Check if return date is after depart date
            if (returnDateObj <= departDateObj) {
                showFlashMessage('Return date must be after depart date.', 'error');
                event.preventDefault();
                return;
            }
            // Check if passengers is between 1-9
            if (passengers < 1 || passengers > 9) {
                showFlashMessage('Number of passengers must be between 1 and 9.', 'error');
                event.preventDefault();
                return;
            }
            else{
                // Show loader
                document.querySelector('.loader').style.display = 'block';
            }
        });
    }

// Handle the flight save button    
    const saveFlightButtons = document.querySelectorAll('.save-flight-btn');
    saveFlightButtons.forEach(button => {
        button.addEventListener('click', async function() {
            try {
                const flightId = button.getAttribute('data-flight-id');
                const response = await fetch(`/flight/${flightId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to save flight data');
                } 
                else {
                    showFlashMessage('Flight saved successfully.', 'success');
                    removeFlight(flightId);
                }
            } catch (error) {
                showFlashMessage('Failed to save flight data: ' + error.message, 'error');
            }
        });
    });
    
// Handle the flight delete button    
    const deleteFlightButtons = document.querySelectorAll('.delete-flight-btn');
    deleteFlightButtons.forEach(button => {
        button.addEventListener('click', async function() {
            try {
                const flightId = button.getAttribute('data-flight-id');
                const response = await fetch(`/flight/${flightId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to delete flight data');
                }
                else {
                    showFlashMessage('Flight successfully deleted.', 'success');
                    removeFlight(flightId);

                }                
            } catch (error) {
                showFlashMessage('Failed to delete flight data: ' + error.message, 'error');
            }
        });
    });
    
// Remove flight from display
    function removeFlight (flightId) {
        const flightElement = document.querySelector(`[data-flight-id="${flightId}"]`);
        if (flightElement && flightElement.parentElement) {
            flightElement.parentElement.remove();
        }    
    }

// Display flash message to user
    function showFlashMessage(message, type = 'success') {
        const flashMessage = document.getElementById('flash-message');
        flashMessage.textContent = message;
        flashMessage.className = type;
        flashMessage.classList.add('show');

        // Hide the message after 3 seconds
        setTimeout(() => {
            flashMessage.classList.remove('show');
        }, 3000);
    }

// Format JSON data duration (PT6H28M to 6 hr 28 min)
    function formatDuration(duration_str) {
        const parts = duration_str.split('T')[1].split('H');
        const hours = parseInt(parts[0]);
        let minutes = 0;
        if (parts[1].includes('M')) {
            minutes = parseInt(parts[1].split('M')[0]);
        }
        return `${hours} hr ${minutes} min`;
    }
        // Get all elements with the 'duration' class
    const durationElements = document.querySelectorAll('.duration');
    // Loop through each element and format its content
    durationElements.forEach(element => {
        const originalText = element.textContent;
        const formattedText = formatDuration(originalText);
        element.textContent = `Duration: ${formattedText}`;
    });
    const totalDurationElements = document.querySelectorAll('.total-duration');
    totalDurationElements.forEach(element => {
        const originalText = element.textContent;
        const formattedText = formatDuration(originalText);
        element.textContent = `Total Duration: ${formattedText}`;
    });

// Format JSON data time ISO 8601 (2023-10-21T13:03:00)
    function formatTime(iso_time) {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const dt = new Date(iso_time);
        const year = dt.getFullYear().toString();
        const month = months[dt.getMonth()];
        const day = dt.getDate();
        const hours = dt.getHours();
        const minutes = dt.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const formattedHours = hours % 12 || 12;
        const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
        return `${month} ${day}, ${year}, ${formattedHours}:${formattedMinutes} ${ampm}`;
    }
    const timeElements = document.querySelectorAll('.time');
    timeElements.forEach(element => {
        const originalText = element.textContent;
        const formattedText = originalText.split(' - ').map(formatTime).join(' - ');
        element.textContent = formattedText;
    });

// Change 0 stop to Non Stop
    const numStopsElements = document.querySelectorAll(".num-stops");
    numStopsElements.forEach((element) => {
        const numStops = element.textContent.trim();
        if (numStops === "0") {
            element.textContent = "Stops: Non-stop";
        } else {
            element.textContent = `Stops: ${numStops}`;
        }
    });

// Convert EUR to USD
    // Get the exchange rate from API or storage
    async function getExchangeRate() {
        // Check if the exchange rate is already in localStorage
        const cachedExchangeRate = localStorage.getItem('exchangeRate');
        if (cachedExchangeRate) {
            return parseFloat(cachedExchangeRate);
        } else {
            // If not in localStorage, fetch it from the API
            try {
                const response = await fetch('https://api.exchangerate-api.com/v4/latest/EUR');
                const data = await response.json();
                const exchangeRate = data.rates.USD;
                // Store the exchange rate in localStorage for future use
                localStorage.setItem('exchangeRate', exchangeRate);
                return exchangeRate;
            } catch (error) {
                console.error('Error fetching exchange rate:', error);
                return 0; // Return 0 in case of an error
            }
        }
    }

    async function convertEURtoUSD(eurAmount) {
        const cacheExchangeRate = await getExchangeRate();
        return eurAmount * cacheExchangeRate;
    }

    (async () => {
        const priceElements = document.querySelectorAll('.price');
        for (let element of priceElements) {
            const EUR = parseFloat(element.textContent); 
            const USD = await convertEURtoUSD(EUR); 
            element.textContent = `Price: $${USD.toFixed(2)} USD`;
        }
    })();

});


// // Function to fetch flights (flightData) using formData (getFormData) / user's input + access token obtained through getToken
//     async function fetchFlights(formData) {
//         // Create the URL with formData
//         const baseUrl = "https://test.api.amadeus.com/v2/shopping/flight-offers";
//         const params = {
//             originLocationCode: formData.departureCity,
//             destinationLocationCode: formData.arrivalCity,
//             departureDate: formData.departDate,
//             returnDate: formData.returnDate,
//             adults: formData.passengers,
//             max: 25
//         };
//         const url = `${baseUrl}?${new URLSearchParams(params).toString()}`;

//         try {
//             const accessToken = sessionStorage.getItem('token');
//             if (!accessToken) {
//                 await getToken();
//                 accessToken = sessionStorage.getItem('token');
//             }
//             const response = await fetch(url, {
//                 headers: {
//                     'Authorization': `Bearer ${accessToken}`,
//                 },
//             });
//             if (!response.ok) {
//                 throw new Error('Failed to fetch flight destinations');
//             }

//             const flightData = await response.json();
//             return flightData;

//         } catch (error) {
//             alert('Failed to fetch flight data: ' + error.message);
//         }
//     }

// // Function to sends flight data to the server as a JSON object
//     async function sendFlightData(flightData) {
//         try {
//             const response = await fetch('/search-results', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(flightData)
//             });

//             if (!response.ok) {
//                 throw new Error('Failed to send flight data');
//             } 

//         } catch (error) {
//             alert('Failed to send flight data: ' + error.message);
//         }
//     };