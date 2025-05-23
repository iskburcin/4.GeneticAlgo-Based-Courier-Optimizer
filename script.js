let destinations = [];
let map;
let selectedLocation = null;
let geocoder;


const myMap = $("map");
// Add New Destination
$("addDestinationBtn")
    .addEventListener("click", function () {
        $("map").classList.add("hidden");
        $("saveDestinationBtn").classList.remove("hidden");
        $("destinationForm").classList.remove("hidden");
        $("addDestinationBtn").classList.add("hidden");
    });

// Select Location from Map
$("selectFromMapBtn")
    .addEventListener("click", function () {
        myMap.classList.remove("hidden");
        initMap();
    });

// Save Destination
$("saveDestinationBtn")
    .addEventListener("click", function () {
        const name = $("destinationName").value;
        const isStart = $("isStart").checked ? 1 : 0;
        const isEnd = $("isEnd").checked ? 1 : 0;
        const address = { lat: selectedLocation.lat(), lang: selectedLocation.lng() };
        console.log(name, isStart, isEnd, address)

        if (!name || !address) {
            alert("Please fill all fields correctly.");
            return;
        }

        // Save the destination to the destinations array
        destinations.push({ name, isStart, isEnd, address });

        $("map").classList.add("hidden");
        $("addDestinationBtn").classList.remove("hidden");
        displayDestinations();

        // Reset the form for the next destination
        $("destinationName").value = "";
        $("address").value = "";
        $("isStart").checked = false;
        $("isEnd").checked = false;
        $("destinationForm").classList.add("hidden");
        $("saveDestinationBtn").classList.add("hidden");
        showEnd();
    });

function $(elem) {
    return document.getElementById(`${elem}`);
}

// Initialize Google Map
function initMap() {
    const gm = google.maps;
    map = new gm.Map(myMap, {
        streetViewControl: false,
        zoom: 14,
        center: { lat: 51.5074, lng: -0.1278 },
    });
    // Create the initial InfoWindow.
    let infoWindow = new gm.InfoWindow({
        content: "Click the map to get Lat/Lng!",
        position: { lat: 51.5074, lng: -0.1278 },
    });
    infoWindow.open(map);
    // Configure the click listener.
    map.addListener("click", (e) => {
        infoWindow.close();
        // Create a new InfoWindow.
        infoWindow = new gm.InfoWindow({
            position: e.latLng,
        });
        infoWindow.setContent(
            JSON.stringify(e.latLng.toJSON(), null, 2),
        );
        infoWindow.open(map);

        selectedLocation = e.latLng;
        $(
            "address"
        ).value = `Lat: ${selectedLocation.lat()}, Lng: ${selectedLocation.lng()}`;
    });
}
function showEnd() {
    console.log(destinations);
    if (Object.keys(destinations).length >= 2) {
        console.log(Object.keys(destinations).length);
        $("endSelectionMap").classList.remove("hidden");
        $("showDestinationsBtn").classList.remove("hidden");
    }
}

// Display Destinations List
function displayDestinations() {
    const list = $("destinationList");
    list.classList.remove("hidden");
    list.innerHTML = ""; // Clear the list

    destinations.forEach((destination, index) => {
        const item = document.createElement("div");
        item.classList.add("destination-item");
        item.innerHTML = `
                    <div><strong>${destination.name}</strong></div>
                    <div>Start: ${destination.isStart ? "Yes" : "No"}</div> <div>End: ${destination.isEnd ? "Yes" : "No"}</div>
                    <div>Address: ${destination.address.lang} | ${destination.address.lat}</div> <br>
                `;
        item.classList.add("set")
        list.appendChild(item);
    });
}
$("endSelectionMap").addEventListener("click", () => {
    $("mapSection").classList.add("hidden");
    $("algoSection").classList.remove("hidden");
})
// Show All Destinations on the Map
$("showDestinationsBtn")
    .addEventListener("click", async function () {
        $("map").classList.remove("hidden");
        const gm = google.maps;
        const { AdvancedMarkerElement } = await gm.importLibrary("marker");

        map = new gm.Map(myMap, {
            streetViewControl: false,
            zoom: 14,
            center: { lat: 51.5074, lng: -0.1278 },
            mapId: "89d1e859f932ffc3 ",
        });
        for (let i = 0; i < Object.keys(destinations).length; i++) {
            console.log("neden" + destinations[i].address.lang);
            var center = new gm.LatLng(destinations[i].address.lat, destinations[i].address.lang)
            var marker = new gm.marker.AdvancedMarkerElement({
                position: center,
                map: map,
            });
            var infowindow = new gm.InfoWindow({});
            var marker, count;

            marker = new gm.marker.AdvancedMarkerElement({
                position: center,
                map: map,
                title: destinations[i].name,
            });
            gm.event.addListener(marker, 'click', (function (marker, count) {
                return function () {
                    infowindow.setContent(locations[count][0]);
                    infowindow.open(map, marker);
                }
            })(marker, count));
        }
    });

$('toggleCrossover').addEventListener('change', function () {
    const crossoverOptions = $('crossoverOptions');
    if (this.checked) crossoverOptions.classList.remove("hidden");
    else crossoverOptions.classList.add("hidden");
});

$('toggleMutation').addEventListener('change', function () {
    const mutationOptions = $('mutationOptions');
    if (this.checked) mutationOptions.classList.remove("hidden");
    else mutationOptions.classList.add("hidden");
});

async function submitData() {
    const form = $('algorithmParams');
    const formData = new FormData(form);
    const algoData = {};

    // Handle Population Size
    algoData.popSize = formData.get('popSize');
    algoData.selectionType = formData.get('selectionType');

    // Handle Crossover
    const isCrossoverEnabled = formData.get('isCrossOver') === 'on';
    if (isCrossoverEnabled) {
        algoData.crossover = {
            type: formData.get('crossoverType'),
            rate: formData.get('crossoverRate'),
        };
    } else {
        algoData.crossover = false;
    }

    // Handle Mutation
    const isMutationEnabled = formData.get('isMutation') === 'on';
    if (isMutationEnabled) {
        algoData.mutation = {
            types: formData.getAll('mutationType'), // Allow multiple mutation types
            rate: formData.get('mutationRate'),
        };
    } else {
        algoData.mutation = false;
    }
    $("destinationList").classList.remove("hidden");
    // Handle Stop Condition
    algoData.stopCondition = formData.get('stopCondition');
    const jsonData = { algoData: algoData, routeData: destinations }
    console.log(JSON.stringify(jsonData))
    // Send data to Flask backend
    fetch('https://four-geneticalgo-based-courier-optimizer.onrender.com/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
    })
        .then(response => response.json())
        .then(data => {
            data.forEach((routeObj, index) => {
                const route = routeObj.route;
                const fitness = routeObj.fitness;
                const color = getRouteColor(index);  // Get color for the route
                drawRoute(route, color);
            });
        })
        .catch(error => console.error('Error fetching routes:', error));

}

function drawRoute(route, color) {
    const coordinates = route.map(point => ({ lat: point.lat, lng: point.lng }));
    let map = new google.maps.Map($('map'), {
        streetViewControl: false,
        zoom: 10,
        center: coordinates[1],
    });

    console.log(`Route: ${coordinates[0].lat}`);
    const path = new google.maps.Polyline({
        path: coordinates,
        geodesic: true,
        strokeColor: color,  // Set color dynamically
        strokeOpacity: 1.0,
        strokeWeight: 4,
    });

    path.setMap(map);
    $('map').classList.remove('hidden');
}

function getRouteColor(index) {
    const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'];
    return colors[index % colors.length];  // Return a color based on the route index
}
// // function displayResults(routes) {
// //     const ctx = $('resultsChart').getContext('2d');
// //     new Chart(ctx, {
// //         type: 'line',
// //         data: {
// //             labels: ['Route 1', 'Route 2', 'Route 3'],
// //             datasets: [{
// //                 label: 'Cost',
// //                 data: routes.map(route => route.cost),
// //                 borderColor: 'rgb(255, 99, 132)',
// //                 fill: false
// //             }]
// //         },
// //         options: {
// //             scales: {
// //                 y: {
// //                     beginAtZero: true
// //                 }
// //             }
// //         }
// //     });
// // }

// // function updateChart() {
// //     // Placeholder for chart update logic
// //     var ctx = $("route-chart").getContext("2d");
// //     new Chart(ctx, {
// //         type: "line",
// //         data: {
// //             labels: ["Route 1", "Route 2", "Route 3"],
// //             datasets: [
// //                 {
// //                     label: "Delivery Cost",
// //                     data: [100, 80, 90],
// //                     borderColor: "rgba(75, 192, 192, 1)",
// //                     borderWidth: 1,
// //                 },
// //                 {
// //                     label: "Travel Time",
// //                     data: [30, 25, 28],
// //                     borderColor: "rgba(153, 102, 255, 1)",
// //                     borderWidth: 1,
// //                 },
// //                 {
// //                     label: "Fuel Consumption",
// //                     data: [15, 12, 13],
// //                     borderColor: "rgba(255, 159, 64, 1)",
// //                     borderWidth: 1,
// //                 },
// //             ],
// //         },
// //     });
// // }

// // document.querySelector("#evolution").addEventListener("click", () => {
// //     startEvolutionProcess();
// // });

// // function startEvolutionProcess() {
// //     // Placeholder for genetic algorithm evolution process
// //     console.log("Starting evolution process...");
// // }