const timesButton = document.getElementById("times");
const rosterButton = document.getElementById("roster");

function sendCommand(id) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {type:id}, function(response){
            console.log(response);
        });
    });
}

timesButton.addEventListener("click", () => {
    sendCommand("times");
});

rosterButton.addEventListener("click", () => {
    sendCommand("roster");
});

