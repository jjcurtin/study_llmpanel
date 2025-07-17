Qualtrics.SurveyEngine.addOnReady(function() {
    var participantID = "${e://Field/ParticipantID}";
    var xhr = new XMLHttpRequest();
    var url = "http://localhost:5000/feedback_survey/access_feedback/" + encodeURIComponent(participantID);
    // change the url to the ngrok one for prod (do not push the url!)

    xhr.open("GET", url, true);
    xhr.setRequestHeader("ngrok-skip-browser-warning", "true");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var jsonResponse = JSON.parse(xhr.responseText);

                    if (jsonResponse.subject_name) {
                        Qualtrics.SurveyEngine.setEmbeddedData("SubjectName", jsonResponse.subject_name);
						Qualtrics.SurveyEngine.setEmbeddedData("LapseLevel", jsonResponse.lapse_level);
						Qualtrics.SurveyEngine.setEmbeddedData("LapseChange", jsonResponse.lapse_change);
						Qualtrics.SurveyEngine.setEmbeddedData("MostImportantFeature", jsonResponse.most_important_feature);
						Qualtrics.SurveyEngine.setEmbeddedData("Message", jsonResponse.message);
                        var newLabel = "Hello, " + jsonResponse.subject_name + ".";
                        
                        if (jsonResponse.status) {
                            newLabel += " " + jsonResponse.status;
                            Qualtrics.SurveyEngine.setEmbeddedData("Status", jsonResponse.status);
                        } else {
                            newLabel += " ERROR";
                        }
						
						newLabel += "<br><br>Your lapse risk is " + jsonResponse.lapse_level + " and " + jsonResponse.lapse_change;
                        newLabel += "<br><br>The most important feature relating to your lapse risk is " + jsonResponse.most_important_feature;
						newLabel += "<br><br>" + jsonResponse.message;
                        jQuery('.QuestionText').html(newLabel);
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