// static/js/main.js – FINAL CLEAN & FULLY WORKING VERSION
// Works with your Django backend + .pkl models
// No TensorFlow.js, no models.json, no weights.bin

let userLat = null;
let userLon = null;
let map = null;

// Hide preloader smoothly when page loads
window.addEventListener("load", () => {
    const preloader = document.getElementById("preloader");
    if (preloader) {
        preloader.style.transition = "opacity 1.5s ease";
        preloader.style.opacity = "0";
        setTimeout(() => {
            preloader.style.display = "none";
        }, 1600);
    }
});

// Get GPS Location
function getLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLat = position.coords.latitude;
            userLon = position.coords.longitude;

            document.getElementById("latField").value = userLat;
            document.getElementById("lonField").value = userLon;

            alert("Location captured successfully!");
            document.getElementById("predictBtn").disabled = false;

            // Show map with user location
            document.getElementById("map").style.display = "block";
            if (!map) {
                map = L.map("map").setView([userLat, userLon], 15);
                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                L.marker([userLat, userLon])
                    .addTo(map)
                    .bindPopup("<b>You are here</b>")
                    .openPopup();
            }
        },
        () => {
            alert("Unable to get location. Please allow location access.");
        }
    );
}

// MAIN FUNCTION: Run AI Diagnosis
async function runPrediction() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a leaf image first!");
        return;
    }

    // Show preview
    const preview = document.getElementById("preview");
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    // Prepare form data
    const formData = new FormData();
    formData.append("image", file);
    if (userLat && userLon) {
        formData.append("lat", userLat);
        formData.append("lon", userLon);
    }

    // Show loader
    document.getElementById("loader").style.display = "block";
    document.getElementById("result").style.display = "none";

    try {
        const response = await fetch("/myapp/api/predict/", {
            method: "POST",
            body: formData
        });

        const text = await response.text(); // Get raw response for debugging
        console.log("Server response:", text);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = JSON.parse(text);

        // SUCCESS — Show results
        document.getElementById("loader").style.display = "none";
        document.getElementById("result").style.display = "block";

        document.getElementById("result").innerHTML = `
            <div class="alert alert-success text-center p-4">
                <h2 class="text-danger">${data.disease}</h2>
                <h5>(${data.swahili})</h5>
                <p><strong>Confidence:</strong> ${data.confidence}%</p>
                <hr>
                <p><strong>Treatment:</strong><br>${data.treatment}</p>
                <p><strong>Recommended Pesticides:</strong><br>
                   <span class="badge bg-warning text-dark px-3 py-1 rounded">${data.pesticides.join(' • ')}</span>
                </p>

                <h5 class="mt-4">Nearby Agrovets</h5>
                ${data.nearby_shops.length > 0
                    ? `<ul class="list-group">
                        ${data.nearby_shops.map(shop => 
                            `<li><strong>${shop.name}</strong><br><small>${shop.address}</small></li>`
                        ).join('')}
                       </ul>`
                    : "<p>No agrovet found nearby</p>"
                }
            </div>
        `;

        // Auto-fill save form (for result page)
        document.getElementById("predicted_label").value = data.disease + " (" + data.swahili + ")";
        document.getElementById("confidence").value = data.confidence;
        document.getElementById("hiddenImage").files = fileInput.files;

        // Optional: Auto-submit to save diagnosis
        // document.getElementById("saveForm").submit();

    } catch (error) {
        document.getElementById("loader").style.display = "none";
        alert("Diagnosis failed: " + error.message + "\nCheck console (F12)");
        console.error("Prediction error:", error);
    }
}