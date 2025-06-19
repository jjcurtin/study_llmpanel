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
                        } else {
                            newLabel += " ERROR.";
                        }
                        
                        jQuery('.QuestionText').text(newLabel);
                    } else {
                        throw new Error("No subject name found in the response.");
                    }
                } catch (e) {
                    jQuery('.QuestionText').text("An error occurred while retrieving your information. Please contact the study coordinators.");
                }
            } else {
                Qualtrics.SurveyEngine.setEmbeddedData("Status", "error");
                jQuery('.QuestionText').text("An error has occurred. Please contact the study coordinators.");
            }
        }
    };
    
    xhr.onerror = function() {
        jQuery('.QuestionText').text("A network error occurred. Please contact the study coordinators.");
    };
    
    xhr.send();
});