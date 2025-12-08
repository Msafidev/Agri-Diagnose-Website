// ===============================
// main.js – FINAL CLEAN VERSION
// Works with Django backend + .pkl ML model
// ===============================

let userLat = null;
let userLon = null;
let map = null;

// PRELOADER
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

// GET GPS LOCATION
function getLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported on this browser");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        pos => {
            userLat = pos.coords.latitude;
            userLon = pos.coords.longitude;

            document.getElementById("latField").value = userLat;
            document.getElementById("lonField").value = userLon;

            alert("Location captured!");

            document.getElementById("predictBtn").disabled = false;

            // Show Map
            document.getElementById("map").style.display = "block";
            if (!map) {
                map = L.map("map").setView([userLat, userLon], 15);
                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: "© OpenStreetMap"
                }).addTo(map);

                L.marker([userLat, userLon])
                    .addTo(map)
                    .bindPopup("<b>You are here</b>")
                    .openPopup();
            }
        },
        () => alert("Failed to get location. Allow GPS access.")
    );
}

// =====================================
// MAIN FUNCTION — RUN AI DIAGNOSIS
// =====================================

async function runPrediction() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Upload a leaf image first!");
        return;
    }

    // Show Preview
    const preview = document.getElementById("preview");
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    // Loader
    document.getElementById("loader").style.display = "block";
    document.getElementById("result").style.display = "none";

    // Prepare request
    const formData = new FormData();
    formData.append("image", file);
    if (userLat) formData.append("lat", userLat);
    if (userLon) formData.append("lon", userLon);

    try {
        const response = await fetch("/myapp/api/predict/", {
            method: "POST",
            body: formData
        });

        const raw = await response.text();
        console.log("Server Response:", raw);

        if (!response.ok) throw new Error("Server returned " + response.status);

        const data = JSON.parse(raw);

        document.getElementById("loader").style.display = "none";
        document.getElementById("result").style.display = "block";

        document.getElementById("result").innerHTML = `
            <div class="alert alert-success text-center p-4">
                <h2 class="text-danger">${data.disease}</h2>
                <h5>${data.swahili}</h5>
                <p><strong>Confidence:</strong> ${data.confidence}%</p>

                <hr>

                <p><strong>Treatment:</strong><br>${data.treatment}</p>

                <p><strong>Pesticides:</strong><br>
                    <span class="badge bg-warning text-dark">${data.pesticides.join(" • ")}</span>
                </p>

                <h5 class="mt-4">Nearby Agrovets</h5>
                ${
                    data.nearby_shops.length > 0
                        ? `<ul class="list-group">
                                ${data.nearby_shops.map(s => `
                                    <li>
                                        <strong>${s.name}</strong><br>
                                        <small>${s.address}</small>
                                    </li>`).join("")}
                           </ul>`
                        : "<p>No agrovet found nearby</p>"
                }
            </div>
        `;

        saveToDatabase(
    `${data.disease} (${data.swahili})`,  // predicted_label
    data.confidence,                      // confidence
    userLat,                              // lat
    userLon,                              // lon
    fileInput.files[0]                    // imageFile (the actual File object!)
);

    } catch (err) {
        document.getElementById("loader").style.display = "none";
        alert("Diagnosis failed: " + err.message);
        console.error(err);
    }
}

// =====================================
// SAVE DIAGNOSIS TO DATABASE
// =====================================

function saveToDatabase(predicted_label, confidence, lat, lon, imageFile) {
    const formData = new FormData();
    formData.append('3', predicted_label);           // ← FIELD NAME MUST BE 'disease'
    formData.append('confidence', confidence);
    if (lat) formData.append('latitude', lat);
    if (lon) formData.append('longitude', lon);
    if (imageFile) formData.append('image', imageFile);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                      document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    fetch("{% url 'save_diagnosis' %}", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken || '',
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
    })
    .then(data => {
        console.log("SAVED TO DATABASE!", data);
        alert("Diagnosis saved successfully!");
    })
    .catch(err => {
        console.error("Save failed:", err);
    });
}