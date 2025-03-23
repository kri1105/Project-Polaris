// js/main.js
$(document).ready(function() {
  let placesService;
  const $venueDivs = [$("#venue1"), $("#venue2"), $("#venue3"), $("#venue4"), $("#venue5")];
  const $weatherDivs = [$("#weather1"), $("#weather2"), $("#weather3"), $("#weather4"), $("#weather5"), $("#weather6"), $("#weather7")];
  const $destination = $("#destination");
  const container = $(".container");


  $('#button').click(function(event) {
      event.preventDefault();

      const city = $('#city').val();

      if (city.trim() === "") {
          alert("Please enter a city name.");
          return;
      }

      container.css("visibility", "visible");

      $venueDivs.forEach(venue => venue.empty());
      $weatherDivs.forEach(day => day.empty());
      $destination.empty();

      if (!placesService) {
          placesService = new google.maps.places.PlacesService(document.createElement('div'));
      }

      const geocoder = new google.maps.Geocoder();
      geocoder.geocode({ 'address': city }, (results, status) => {
        if (status === 'OK' && results && results[0] && results[0].geometry && results[0].geometry.location) { // Check all the way down
          const location = results[0].geometry.location;
          const latitude = location.lat();
          const longitude = location.lng();

              fetch(`/api/places?lat=${latitude}&lng=${longitude}&query=attractions in ${city}`)
                  .then(response => {
                      if (!response.ok) {
                          throw new Error(`HTTP error! status: ${response.status}`);
                      }
                      return response.json();
                  })
                  .then(data => {
                      console.log("Google Places Data:", data);
                      if (data.status === "OK" && data.results) {
                          $venueDivs.forEach(($venue, index) => {
                              if (index < data.results.length) {
                                  const place = data.results[index];
                                  const venueContent = createVenueHTML(place.name, place.vicinity, place.icon);
                                  $venue.empty().append(venueContent);
                              } else {
                                  $venue.empty();
                              }
                          });
                      } else {
                        console.error("Geocoding failed:", status);
                        if (results && results.length > 0) {
                            console.error("Geocoding results:", results);
                        }
                        alert("Could not find location.");
                    }
                });

              fetch(`/api/weather?city=${city}`)
                  .then(response => {
                      if (!response.ok) {
                          throw new Error(`HTTP error! status: ${response.status}`);
                      }
                      return response.json();
                  })
                  .then(data => {
                      console.log("Weather Data:", data);
                      if (data.forecast && data.forecast.forecastday) {
                          renderForecast(data.forecast.forecastday);
                      } else {
                          console.error("Invalid weather data format:", data);
                          alert("Error fetching weather data. Please try again.");
                      }
                  })
                  .catch(error => {
                      console.error("Error fetching weather:", error);
                      alert("Error fetching weather data. Please try again.");
                  });

          } else {
              console.error("Geocoding failed:", status);
              $venueDivs.forEach(venue => venue.empty());
              alert("Could not find location.");
          }
      });

      $destination.append(`<h2>${city}</h2>`);

  });


  const createVenueHTML = (name, address, iconSource) => {
      return `<h2>${name}</h2>
      <img class="venueimage" src="${iconSource}" alt="Venue Icon"/>
      <h3>Address:</h3>
      <p>${address || "Not available"}</p>`;
  };

  const renderForecast = (forecastDays) => {
      $weatherDivs.forEach(($day, index) => {
          if (index < forecastDays.length) {
              const currentDay = forecastDays[index];
              const weatherContent = createWeatherHTML(currentDay);
              $day.empty().append(weatherContent);
          }
      });
  };

  const createWeatherHTML = (currentDay) => {
      return `<h2> High: ${currentDay.day.maxtemp_c}</h2>
      <h2> Low: ${currentDay.day.mintemp_c}</h2>
      <img src="https:${currentDay.day.condition.icon}" class="weathericon" alt="Weather Icon"/>
      <h2>${weekDays[(new Date(currentDay.date)).getDay()]}</h2>`;
  };

  const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

});