document.addEventListener("DOMContentLoaded", async function () {
    flatpickr('.flatpickr-input');

    const token = await fetchToken();
    const weather_token = await fetchWeatherToken();

// Fetch token from Python/Server
    async function fetchToken() {
        try {
            const response = await fetch('/token');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            return data.token;
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }

// Fetch weather_token from Python/Server
    async function fetchWeatherToken() {
        try {
            const response = await fetch('/token');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            return data.weather_token;
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }

// Fetch suggestions based on user input for locations
    const suggestionsCache = {};
    async function fetchSuggestions(userInput) {
        if (userInput.length >= 3) {
            if (suggestionsCache[userInput]) {
                return suggestionsCache[userInput];
            }
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
                suggestionsCache[userInput] = data.data;
                return data.data 
            } catch (error) {
                console.error('Error fetching data:', error);
                return [];
            }
        } else {
            return [];
        }
    }

    function showSuggestions(suggestionsElementId, suggestionsData) {
        const suggestionsContainer = document.getElementById(suggestionsElementId);
        suggestionsContainer.innerHTML = suggestionsData.map(suggestion => {
            return `<div class="suggestion-item" data-name="${suggestion.name}" data-latitude="${suggestion.geoCode.latitude}" data-longitude="${suggestion.geoCode.longitude}" 
            data-iatacode="${suggestion.iataCode}">${suggestion.iataCode} - ${suggestion.name}</div>`;
        }).join('');
        if (suggestionsData.length == 0) { 
            suggestionsContainer.style.display = 'none';
        }
    }
    
    function selectSuggestion(suggestionsElementId, name, latitude, longitude, iatacode) {
        document.getElementById(suggestionsElementId.replace('_location_suggestions', '_name')).value = name;
        document.getElementById(suggestionsElementId.replace('_location_suggestions', '_lat')).value = latitude;
        document.getElementById(suggestionsElementId.replace('_location_suggestions', '_long')).value = longitude;
        document.getElementById(suggestionsElementId.replace('_location_suggestions', '_iatacode')).value = iatacode;
        document.getElementById(suggestionsElementId).style.display = 'none';
    }

// Handle user interactions related to the input fields for lcoation suggestions
    function setupAutocomplete(inputElementId, suggestionsElementId) {
        const inputElement = document.getElementById(inputElementId);
        const suggestionsContainer = document.getElementById(suggestionsElementId);
        let timeoutId;
        let blurTimeoutId; 
        let isMouseInsideInput = false;
        if (inputElement) {
            inputElement.addEventListener('input', async function () {
                clearTimeout(timeoutId);
                clearTimeout(blurTimeoutId);
                timeoutId = setTimeout(async () => {
                        const userInput = this.value;
                        suggestionsData = await fetchSuggestions(userInput);
                        showSuggestions(suggestionsElementId, suggestionsData);
                        if (isMouseInsideInput && userInput.length >= 3 && suggestionsContainer.children.length > 0) {
                            suggestionsContainer.style.display = 'block';
                        }
                }, 700);
            });
            inputElement.addEventListener('blur', async function () {
                blurTimeoutId = setTimeout(() => {
                    if (document.activeElement !== inputElement) {
                        suggestionsContainer.style.display = 'none';
                        isMouseInsideInput = false;
                    }
                }, 200);
            });
            inputElement.addEventListener('focus', function () {
                isMouseInsideInput = true;
            });
        }
        if (suggestionsContainer) {
            suggestionsContainer.addEventListener('click', function (event) {
                const clickedElement = event.target;
                if (clickedElement.classList.contains('suggestion-item')) {
                    document.getElementById(suggestionsElementId.replace('_suggestions', '')).value = `${clickedElement.dataset.name}`;
                    selectSuggestion(suggestionsElementId, clickedElement.dataset.name, clickedElement.dataset.latitude, clickedElement.dataset.longitude, clickedElement.dataset.iatacode);
                }
            });
        }
    }

    setupAutocomplete('departure_location', 'departure_location_suggestions');
    setupAutocomplete('arrival_location', 'arrival_location_suggestions');

// Handle cases where user types in a valid airport, city or iatacode. Fetch and populate hidden attributes in html
    async function handleUserInput(userInput, suggestionsElementId) {
        const suggestionsContainer = document.getElementById(suggestionsElementId);
        suggestionsData = await fetchSuggestions(userInput);
        showSuggestions(suggestionsElementId, suggestionsData);
        document.getElementById(suggestionsElementId).style.display = 'none';
        if (userInput.trim() === '') {
            selectSuggestion(suggestionsElementId, userInput, 0, 0, userInput);
            return false;
        }
        else if (userInput.length == 1 || userInput.length == 2) {
            selectSuggestion(suggestionsElementId, userInput, 0, 0, userInput);
            return false;
        } else {
            const matchedDiv = suggestionsContainer.querySelector(`.suggestion-item[data-name="${userInput}"], .suggestion-item[data-iatacode="${userInput}"]`);
            if (matchedDiv) {
                const name = matchedDiv.getAttribute('data-name');
                const latitude = matchedDiv.getAttribute('data-latitude');
                const longitude = matchedDiv.getAttribute('data-longitude');
                const iataCode = matchedDiv.getAttribute('data-iatacode');
                selectSuggestion(suggestionsElementId, name, latitude, longitude, iataCode);
                return true;
            } else {
                selectSuggestion(suggestionsElementId, userInput, 0, 0, userInput);
                return false;
            }
        }
    }

    function handleValidationFailure(message, event) {
        showFlashMessage(message, 'error');
        event.preventDefault();
    }
    
// Client side validation on search form data
    const searchForm = document.querySelector("#flight-search-form");  
    if (searchForm) {
        searchForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const departureCity = document.getElementById("departure_location").value;
            const arrivalCity = document.getElementById("arrival_location").value;
            const departDate = document.getElementById("depart_date").value;
            const returnDate = document.getElementById("return_date").value;
            const passengers = document.getElementById("passengers").value;

            const isDepartureValid = await handleUserInput(departureCity, 'departure_location_suggestions');
            if (!isDepartureValid) {
                handleValidationFailure('The airport, city, or IATA code you entered for "From" is either not supported or not found in our database. Please check your entry or try a different location.', event);
                return;
            }
            const isArrivalValid = await handleUserInput(arrivalCity, 'arrival_location_suggestions');
            if (!isArrivalValid) {
                handleValidationFailure('The airport, city, or IATA code you entered for "To" is either not supported or not found in our database. Please check your entry or try a different location.', event);
                return;
            }
            const departureCode = document.getElementById("departure_iatacode").value;
            const arrivalCode = document.getElementById("arrival_iatacode").value;
            function isValidString(str) {
                return /^[a-zA-Z\s]+$/.test(str);
            }
            if (departureCode == arrivalCode) {
                handleValidationFailure('The airport, city, or IATA code you entered for "From" and "To" can not be the same.', event);
                return;
            } 
            if (!isValidString(departureCity)) {
                handleValidationFailure('"From" must contain only alphabetic characters.', event);
                return;
            }  
            if (!isValidString(arrivalCity)) {
                handleValidationFailure('"To" must contain only alphabetic characters.', event);
                return;
            } 
            function isValidDate(date) {
                const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
                return dateRegex.test(date);
            }
            if (!isValidDate(departDate)) {
                handleValidationFailure('Depart date must be in the format YYYY-MM-DD.', event);
                return;
            } 
            if (!isValidDate(returnDate)) {
                handleValidationFailure('Return date must be in the format YYYY-MM-DD.', event);
                return;
            } 
            function parseDateString(dateString) {
                const [year, month, day] = dateString.split('-').map(Number);
                return new Date(year, month - 1, day);
            }
            const departDateObj = parseDateString(departDate);
            const returnDateObj = parseDateString(returnDate);
            let today = new Date();
            today.setHours(0, 0, 0, 0);
            if (departDateObj <= today) {
                handleValidationFailure('Depart date must be tomorrow or later.', event);
                return;
            }
            if (returnDateObj <= departDateObj) {
                handleValidationFailure('Return date must be after depart date.', event);
                return;
            }
            if (passengers < 1 || passengers > 9) {
                handleValidationFailure('Number of passengers must be between 1 and 9.', event);
                return;
            }
            else {
                document.querySelector('.loader').style.display = 'block';
                searchForm.submit();
                searchForm.reset();
                const arrival_lat = document.getElementById("arrival_lat").value;
                const arrival_long = document.getElementById("arrival_long").value;
                const weatherData = await fetchWeather(`${arrival_lat},${arrival_long}`, departDate, returnDate);
                sessionStorage.setItem("weatherData", JSON.stringify(weatherData));
            }
        });
    }

// Show weather data for search result flight
    if (window.location.pathname === "/submit") {
        const weatherData = JSON.parse(sessionStorage.getItem("weatherData"));
        if (weatherData) {
            const searchWeatherContainer = document.querySelector('.search-weather-container');
            const days = weatherData.days;
            days.forEach(day => {
                const dayContainer = document.createElement('div');
                dayContainer.className = 'day-weather';
                const date = document.createElement('p');
                date.textContent = formatDate(day.datetime);
                const temp = document.createElement('p');
                temp.textContent = `Average Temp: ${day.temp}°F`;
                const conditions = document.createElement('p');
                conditions.textContent = `Conditions: ${day.conditions}`;
                const textContainer = document.createElement('div');
                textContainer.className = 'weather-text-container';
                textContainer.appendChild(date);
                textContainer.appendChild(temp);
                textContainer.appendChild(conditions);
                dayContainer.appendChild(textContainer); 
                const weatherIcon = getWeatherIconImage(day.icon)
                dayContainer.appendChild(weatherIcon);
                const tempMaxMin = document.createElement('p');
                tempMaxMin.innerHTML = `<strong>${Math.round(day.tempmax)}°</strong> ${Math.round(day.tempmin)}°`;
                tempMaxMin.className = 'max-min';
                dayContainer.appendChild(tempMaxMin);
                searchWeatherContainer.appendChild(dayContainer);
            });
        } else {
            console.error('Weather data not found in session storage.');
        }
    }

 // Show weather data for saved flights
    const savedFlights = document.querySelectorAll('.saved-flight-container');
    savedFlights.forEach(async flight => {
        const latLong = flight.querySelector('.arrivalLatLong').textContent;
        const daysText = flight.querySelector('.days').textContent;
        const dates = daysText.split(' - ');
        const depart = dates[0].split(' ')[0];
        const returnDate = dates[1].split(' ')[0];

        const weatherData = await fetchWeather(latLong, depart, returnDate);
        displayWeather(weatherData, flight);
    });

    function getWeatherIconImage(iconText) {
        const iconUrl = `/static/weather-icons/${iconText}.png`;
        const weatherIconImage = document.createElement('img');
        weatherIconImage.src = iconUrl;
        return weatherIconImage;
    }

    async function fetchWeather(latLong, depart, returnDate) {
        const cacheKey = `weather-${latLong}-${depart}-${returnDate}`;
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
            return Promise.resolve(JSON.parse(cachedData));
        } else {
            try {
                const url = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${latLong}/${depart}/${returnDate}?unitGroup=us&include=days&key=${weather_token}&contentType=json`;
                const response = await fetch(url);
                if (!response.ok) {
                    if (response.status === 429) {
                        throw new Error('Too Many Requests. Please try again later.');
                    } else {
                        throw new Error(`Failed to fetch weather data. Status: ${response.status}`);
                    }
                }
                const data = await response.json();
                try {
                    localStorage.setItem(cacheKey, JSON.stringify(data));
                }
                catch (error) {
                    if (error.name === 'QuotaExceededError' || error.code === 22) {
                        localStorage.clear();
                        try {
                            localStorage.setItem(cacheKey, JSON.stringify(data));
                            console.log('LocalStorage cleared due to quota exceeded. Retrying...');
                        } catch (retryError) {
                            console.error('Error setting data in LocalStorage after retry:', retryError.message);
                        }
                    } else {
                        console.error('Error setting data in LocalStorage:', error.message);
                    }
                }
                return data;
            } catch (error) {
                console.error('Error fetching weather data:', error);
                throw error;
            }
        }
    }

    function displayWeather(data, flight) {
        const days = data.days;
        days.forEach(day => {
            const dayContainer = document.createElement('div');
            dayContainer.className = 'day-weather';
            const date = document.createElement('p');
            date.textContent = formatDate(day.datetime);;
            const temp = document.createElement('p');
            temp.textContent = `Average Temp: ${day.temp}°F`;
            const conditions = document.createElement('p');
            conditions.textContent = `Conditions: ${day.conditions}`;
            const textContainer = document.createElement('div');
            textContainer.className = 'weather-text-container';
            textContainer.appendChild(date);
            textContainer.appendChild(temp);
            textContainer.appendChild(conditions);
            dayContainer.appendChild(textContainer); 
            const weatherIcon = getWeatherIconImage(day.icon)
            dayContainer.appendChild(weatherIcon);
            const tempMaxMin = document.createElement('p');
            tempMaxMin.innerHTML = `<strong>${Math.round(day.tempmax)}°</strong> ${Math.round(day.tempmin)}°`;
            tempMaxMin.className = 'max-min';
            dayContainer.appendChild(tempMaxMin);
            flight.querySelector('.weather-container').appendChild(dayContainer);
        });
    }

// Handle the flight save button    
    const saveFlightButtons = document.querySelectorAll('.save-flight-btn');
    saveFlightButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const numStopsValue = document.querySelector('.num-stops').dataset.numStops;
            const durationValue = document.querySelector('.total-duration').dataset.totalDuration;
            const priceValue = document.querySelector('.price').dataset.price;
            const flightId = document.querySelector('.flight-id').dataset.flightId;
            try {
                // Perform an AJAX request using the Fetch API
                const response = await fetch('/save_flight', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        flight_id: flightId,
                        numStopsValue: numStopsValue,
                        durationValue: durationValue,
                        priceValue: priceValue
                    }),
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                else {
                    showFlashMessage('Flight successfully saved.', 'success');
                    const flightContainer = button.closest('.flight-container');
                    flightContainer.remove();
                }
            } catch (error) {
                console.error('Fetch error:', error);
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
                    flightContainer = button.closest('.saved-flight-container');
                    flightContainer.remove();
                }                
            } catch (error) {
                showFlashMessage('Failed to delete flight data: ' + error.message, 'error');
            }
        });
    });


// Display flash message to user
    function showFlashMessage(message, type = 'success') {
        const flashMessage = document.getElementById('flash-message');
        flashMessage.textContent = message;
        flashMessage.className = type;
        flashMessage.classList.add('show');
        const timePerChar = 40; 
        let displayTime = message.length * timePerChar;
        const minDisplayTime = 3000;
        displayTime = Math.max(displayTime, minDisplayTime);
        setTimeout(() => {
            flashMessage.classList.remove('show');
        }, displayTime);
    }

// Format flight duration from JSON data (e.g., PT6H28M to 6 hr 28 min)
    function formatDuration(duration_str) {
        if (duration_str && typeof duration_str === 'string' && duration_str.includes('PT')) {
            const regex = /PT(\d+H)?(\d+M)?/;
            const match = duration_str.match(regex);
            if (match) {
                const hours = match[1] ? parseInt(match[1]) : 0;
                const minutes = match[2] ? parseInt(match[2]) : 0;
                return `${hours} hr ${minutes} min`;
            }
        }
        return 'Invalid duration';
    }
    const durationElements = document.querySelectorAll('.duration');
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

// Format JSON data time ISO 8601 (2023-10-21T13:03:00) to Oct 21, 2023, 1:03 PM
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

// Function to format date data ("2024-01-12") to Jan 12, Mon
    function formatDate(dateString) {
        const months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ];
        const dateParts = dateString.split('-');
        if (dateParts.length === 3) {
            const year = dateParts[0];
            const month = parseInt(dateParts[1], 10);
            const day = parseInt(dateParts[2], 10);

            if (!isNaN(month) && !isNaN(day) && month >= 1 && month <= 12 && day >= 1 && day <= 31) {
                const date = new Date(`${year}-${month}-${day}`);
                const dayOfWeek = getDayOfWeek(date);
                const formattedDate = `${months[month - 1]} ${day}, ${dayOfWeek}`;
                return formattedDate;
            }
        }
        return dateString;
    }

    function getDayOfWeek(date) {
        const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return daysOfWeek[date.getUTCDay()];
    }


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

// Convert EUR to USD - Get the exchange rate from API or storage
    async function getExchangeRate() {
        const cachedExchangeRate = localStorage.getItem('exchangeRate');
        if (cachedExchangeRate) {
            return parseFloat(cachedExchangeRate);
        } else {
            try {
                const response = await fetch('https://api.exchangerate-api.com/v4/latest/EUR');
                const data = await response.json();
                const exchangeRate = data.rates.USD;
                localStorage.setItem('exchangeRate', exchangeRate);
                return exchangeRate;
            } catch (error) {
                console.error('Error fetching exchange rate:', error);
                return 0;
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

    document.querySelector('.loader').style.display = 'none';
});
