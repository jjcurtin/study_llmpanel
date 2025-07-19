Qualtrics.SurveyEngine.addOnReady(function () {
    const participantID = "${e://Field/ParticipantID}";
    const container = this.getQuestionTextContainer();
    const feedbackInputs = [];

    container.innerHTML = ""; // Clear default text

    // Add Leaflet CSS
    console.log("Adding Leaflet CSS and JS for maps");
    const leafletCSS = document.createElement("link");
    leafletCSS.rel = "stylesheet";
    leafletCSS.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(leafletCSS);

    // Add Leaflet JS
    const leafletJS = document.createElement("script");
    leafletJS.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    leafletJS.onload = fetchCoordsAndRender;
    document.head.appendChild(leafletJS);

    function fetchCoordsAndRender() {
        const xhr = new XMLHttpRequest();
        const url = "http://localhost:5000/EMA/request_coords/" + encodeURIComponent(participantID);

        xhr.open("GET", url, true);
        console.log("Requesting coordinates from:", url);
        xhr.setRequestHeader("ngrok-skip-browser-warning", "true");
        
        xhr.timeout = 5000; // Set timeout to 5 seconds for testing
        xhr.ontimeout = function () {
            console.error("Request timed out after 5 seconds.");
            container.innerHTML = "<p>Request timed out. Please try again or contact support.</p>";
        };

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (!Array.isArray(response)) throw new Error("Expected an array");

                        const coords = response.map(entry => ({
                            lat: entry.latitude,
                            lng: entry.longitude
                        }));

                        Qualtrics.SurveyEngine.setEmbeddedData("CoordCount", coords.length);
                        renderLeafletMaps(coords);
                    } catch (err) {
                        console.error("Error parsing response:", err);
                        container.innerHTML = "<p>Error loading map coordinates. Please contact support.</p>";
                    }
                } else {
                    container.innerHTML = "<p>Failed to retrieve coordinates (HTTP " + xhr.status + ").</p>";
                }
            }
        };

        xhr.onerror = () => {
            container.innerHTML = "<p>Network error. Please check your connection.</p>";
        };

        xhr.send();
    }

    function renderLeafletMaps(coords) {
        coords.forEach((coord, index) => {
            const group = document.createElement("div");
            group.style.marginBottom = "25px";

            const mapDiv = document.createElement("div");
            mapDiv.id = `map${index}`;
            mapDiv.style.width = "100%";
            mapDiv.style.height = "300px";
            group.appendChild(mapDiv);

            const input = document.createElement("input");
            input.type = "text";
            input.placeholder = `Feedback for location ${index + 1}`;
            input.style.width = "100%";
            input.dataset.index = index;
            group.appendChild(input);

            container.appendChild(group);
            feedbackInputs.push(input);

            const map = L.map(mapDiv.id).setView([coord.lat, coord.lng], 13);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            L.marker([coord.lat, coord.lng]).addTo(map);
        });
    }

    this.questionclick = function (event, element) {
        if (element.type === "NextButton") {
            feedbackInputs.forEach((input, i) => {
                // set the text entry input value to the responses for each feedback input
                for (let j = 0; j < feedbackInputs.length; j++) {
                    const inputValue = feedbackInputs[j].value.trim();
                    if (inputValue) {
                        jQuery('.QuestionBody').append((j + 1) + " " + inputValue + "<br>");
                    }
                }
                Qualtrics.SurveyEngine.setEmbeddedData(`feedback${i + 1}`, input.value || "");
            });
        }
    };
});