Qualtrics.SurveyEngine.addOnUnload(function() {
    var participantID = "${e://Field/ParticipantID}";
    var subjectName = "${e://Field/SubjectName}";
    var xhr = new XMLHttpRequest();
    var url = "http://localhost:5000/EMA/submit_ema";
    // change the url to the ngrok one for prod (do not push the url!)
    
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("ngrok-skip-browser-warning", "true");

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log("EMA submission successful:", xhr.responseText);
        } else if (xhr.readyState === 4) {
            console.error("EMA submission failed. Status:", xhr.status);
        }
    };
    
    var data = JSON.stringify({
        "participantID": participantID,
        "subjectName": subjectName
    });
    
    xhr.send(data);
});