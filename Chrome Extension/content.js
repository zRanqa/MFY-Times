const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

const monthToNum = {
    "Januray": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

const dayToNum = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

function downloadJSON(data, fileName) {
    console.log(data);
    const blob = new Blob([JSON.stringify(data)], {type: 'text/json'});
    const a = document.createElement('a');
    a.href = window.URL.createObjectURL(blob);
    a.download = `${fileName}.json`;
    a.click();
}

function timeTo24H(value) {
    const meridian = value.slice(-2);
    let time = parseInt(value.slice(0, -2))

    if (meridian == 'pm' && time != 12) {
        time += 12
    } else if (meridian == 'am' && time == 12) {
        time = 0;
    }

    return time.toString()
}

function round24HTime(value, up) {
    let hour = parseInt(value.split(":")[0])
    const min = parseInt(value.split(":")[1])

    if (min != 0) {
        if (up) {
            hour++;
            if (hour == 24) hour = 0;
        }
    }

    return hour.toString()
}

function findMFY() {
    let data = [];
    // const table = document.querySelector("#app > div:nth-child(3) > div > div.snapshotDrillthruGrid.dx-widget.dx-visibility-change-handler > div > div.dx-bordered-bottom-view.dx-datagrid-rowsview.dx-datagrid-nowrap.dx-scrollable.dx-visibility-change-handler.dx-scrollable-both.dx-scrollable-simulated.dx-last-row-border > div > div > div.dx-scrollable-content > div > table > tbody")
    const table = document.querySelectorAll("tbody")[1];
    for (let i = 0; i < table.children.length - 2; i++) {
        const row = table.children[i];
        const timeString = row.children[0].textContent;
        const MFY = row.children[5].textContent;
        const timeParts = timeString.split(" ");
        let tableData = {
            start: timeTo24H(timeParts[0]),
            end: timeTo24H(timeParts[2]),
            MFY
        };
        if (MFY != '0' && MFY != '-') {
            data.push(tableData);
        };
    }

    const rawDate = document.querySelector("#app > div.layout > div.subTitleText");
    const date = rawDate.textContent.split(" ")[0];

    downloadJSON(data, `${date.padStart(2, '0')}-MFY`);
}

function formatDate(dateString) {
    date = dateString.replaceAll(",", "").split(" ");
    year = date[3];
    day = date[2];
    month = monthToNum[date[1]];
    return {
        dayName: date[0],
        date: `${year}-${month}-${day}`
    }
}

function decrementDate(dateString) {
    date = dateString.split("-");
    year = date[0];
    month = date[1];
    day = date[2];
    day -= 1;
    if (day <= 0) {
        month -= 1;
        if (month <= 0) {
            month = 12
            year -= 1
        }
        day = daysInMonth[month - 1]
    }
    return `${year}-${month}-${day}`

}


function findRosters() {
    let data = [];
    let difference = 0;
    for (let i = 0; i < 7; i++) {
        const dateString = document.querySelector(`#roster-linebars-report > table:nth-child(${3 + i - difference}) > thead > tr:nth-child(1) > th`);
        const table = document.querySelector(`#roster-linebars-report > table:nth-child(${3 + i - difference}) > tbody:nth-child(3)`);
        document.querySelector("#roster-linebars-report > table:nth-child(4) > tbody:nth-child(3)")
        
        
        date = formatDate(dateString.textContent);

        let tableData = {
            date: date["date"],
            data: []
        };
        if (dayToNum[date["dayName"]] != i) {
            tableData.date = decrementDate(date["date"])
            difference += 1
        }
        else {
        // console.log(`I = ${i}, Date = ${date}`)
            for (let i = 1; i < table.children.length; i++) {
                const row = table.children[i];
                const name = row.children[0].textContent.replaceAll("\n", "").replaceAll("*", "").replaceAll(".","").trim();
                const timeString = row.children[1].textContent;
                const timeParts = timeString.split(" ");
                tableData.data.push({
                    name,
                    start: round24HTime(timeParts[0], false),
                    end: round24HTime(timeParts[2], true)
                });
            }
        }
        data.push(tableData);
    }
    downloadJSON(data, "roster");
}

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {
        switch(message.type) {
            case "roster":
                findRosters()
                break;
            case "times":
                findMFY()
                break;
            default:
                    break;
        }
        sendResponse(message.type)
    }
);