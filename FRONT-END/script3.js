document.getElementById('stepsButton').addEventListener('click', function() {
    var stepsList = document.getElementById('stepsList');
    if (stepsList.style.display === 'none' || stepsList.style.display === '') {
        stepsList.style.display = 'block';
    } else {
        stepsList.style.display = 'none';
    }
});

// Mobile menu toggle
document.getElementById('menuIcon').addEventListener('click', function() {
    var navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
});

// Initialize the map
const map = L.map("map").setView([20.5937, 78.9629], 5); // Default center: India

// Add OpenStreetMap tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
}).addTo(map);

// Function to draw the route
function drawRoute(route) {
    if (window.routeLayer) {
        map.removeLayer(window.routeLayer);
    }

    const routePoints = route.points.coordinates.map(coord => L.latLng(coord[1], coord[0]));
    window.routeLayer = L.polyline(routePoints, { color: "blue" }).addTo(map);
    map.fitBounds(window.routeLayer.getBounds());
}

// Handle form submission
document.getElementById("fromInput").addEventListener("change", updateRoute);
document.getElementById("toInput").addEventListener("change", updateRoute);

function updateRoute() {
    const start = document.getElementById("fromInput").value;
    const end = document.getElementById("toInput").value;

    if (!start || !end) return;

    fetch(`/api/map/route/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            document.getElementById("distanceValue").innerText = (data.distance / 1000).toFixed(1);
            document.getElementById("etaValue").innerText = `${Math.floor(data.time / 3600)}h ${Math.floor((data.time % 3600) / 60)}m`;

            const stepsList = document.getElementById("routeSteps");
            stepsList.innerHTML = data.instructions.map(i => `<li>${i.text} (${(i.distance / 1000).toFixed(1)} km)</li>`).join("");

            drawRoute(data.paths[0]);
        })
        .catch(error => alert("Failed to fetch route: " + error.message));
}
