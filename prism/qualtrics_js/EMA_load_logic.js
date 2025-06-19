Qualtrics.SurveyEngine.addOnReady(function() { 
    var participantID = "${e://Field/ParticipantID}";
    var xhr = new XMLHttpRequest();
    var url = "" + encodeURIComponent(participantID); // add in url to ngrok tunnel here

    xhr.open("GET", url, true);

    xhr.setRequestHeader("ngrok-skip-browser-warning", "true");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var jsonResponse = JSON.parse(xhr.responseText);

                    if (jsonResponse.subject_name) {
                        Qualtrics.SurveyEngine.setEmbeddedData("SubjectName", jsonResponse.subject_name);

                        var newLabel = "Hello, " + jsonResponse.subject_name;
                        
                        if (jsonResponse.status) {
                            newLabel += ". " + jsonResponse.status;
                            Qualtrics.SurveyEngine.setEmbeddedData("Status", jsonResponse.status);
                            console.log("Status updated to:", jsonResponse.status);
                        } else {
                            newLabel += " ERROR.";
                            console.error("No status found in the response.");
                        }
                        
                        jQuery('.QuestionText').text(newLabel);
                        console.log("Subject name updated to:", jsonResponse.subject_name);
                    } else {
                        throw new Error("No subject name found in the response.");
                    }
                } catch (e) {
                    console.error("Error parsing JSON response or missing data:", e);
                    jQuery('.QuestionText').text("An error occurred while retrieving your information. Please contact the study coordinators.");
                }
            } else {
                console.error("Failed to retrieve subject_name or status. HTTP Status:", xhr.status);
				Qualtrics.SurveyEngine.setEmbeddedData("Status", "error");
                jQuery('.QuestionText').text("An error occurred (HTTP Status: " + xhr.status + "). Please contact the study coordinators.");
            }
        }
    };
    
    xhr.onerror = function() {
        console.error("Request failed due to a network error.");
        jQuery('.QuestionText').text("A network error occurred. Please contact the study coordinators.");
    };

    xhr.send();
});