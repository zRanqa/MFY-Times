
// scrape_utils HAS to be loaded first

chrome.runtime.onMessage.addListener(
    async function(message, sender, sendResponse) {
        switch(message.type) {
            case "roster":
                await findRosters();
                break;
            case "times":
                await findMFY();
                break;
            default:
                break;
        }
        sendResponse(message.type);
        return true;
    }
);