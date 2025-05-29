import os
import json

WEIGHTED_LINE_LIST = [
    "Kayleb Wilden",
    "Edan McLean",
    "Jamil Taleb",
    "Tyson Webb",
    "Frankie Brar",
    "Levent Orcan"
    "Kyle Mawer",
    "Ben Dummett",
    "Sarah Essery",
    "William Nicholls",
    "Max Kershaw",
    "Romaric Kabayija-Zawadi",
    "Edwin Thomas",
    "Reebhav Chopra",
    "Lucinda Parker",
    "Niral Maharaj",
    "PJ Burgio-Spooner"
    "Noelle DI Paolo",
    "Pheonix Di Sarno",
    "Ria Patil"
]

def getRosterFromDate(date: str):
    try:
        f = open(f'data/{date}/roster.json', "r")
        roster_data = json.loads(f.read())
        f.close()
        return roster_data
    except:
        return False

def getMFYFromDate(date: str, folder_date: str):
    try:
        mfyData = date.split('-')
        f = open(f'data/{folder_date}/{mfyData[2]}-MFY.json', "r")
        mfyData = json.loads(f.read())
        f.close()
        return mfyData
    except:
        return False

def sortByAverage(dataList):
    for i in range(0,len(dataList)):
        min_index = i
        for j in range(i+1, len(dataList)):
            if dataList[j]["mfy_average"] < dataList[min_index]["mfy_average"]:
                min_index = j

        temp_val = dataList[i]
        dataList[i] = dataList[min_index]
        dataList[min_index] = temp_val

    return dataList

def createTemplateData(roster):
    
    # Create Roster list with unique names and 0 MFY time
    total_mfy_data = []
    for i in range(0, len(roster)):
        for j in range(0, len(roster[i]["data"])):
            nameInData = False
            for k in range(0, len(total_mfy_data)):
                if roster[i]["data"][j]["name"] == total_mfy_data[k]["name"]:
                    nameInData = True
            if nameInData == False and roster[i]["data"][j]["name"] != "":
                total_mfy_data.append({
                    "name": roster[i]["data"][j]["name"],
                    "mfy_total": 0,
                    "mfy_count": 0,
                    "mfy_average": 0})
    return total_mfy_data


def checkWorkersInHour(roster, i, mfy, j):
    try:
        # foundLIST index 0 = count
        foundList = [0]
        for k in range(0, len(roster[i]["data"])):
            if (int(roster[i]["data"][k]["start"]) <= int(mfy[j]["start"])) and (int(roster[i]["data"][k]["end"]) >= int(mfy[j]["end"])):
                foundList.append(roster[i]["data"][k]["name"])
                foundList[0] += 1

        # Sort in order from WEIGHTED_LINE_LIST
        swapIndex = 1
        for k in range(0, len(WEIGHTED_LINE_LIST)):
            for l in range(swapIndex, len(foundList)):
                if WEIGHTED_LINE_LIST[k] == foundList[l]:
                    temp = foundList[swapIndex]
                    foundList[swapIndex] = foundList[l]
                    foundList[l] = temp
                    swapIndex += 1
        return foundList
    except:
        return False

def calculate_data(date: str) -> list[dict[str, int]]:
    """
    Returns the calculated data of everyone mfy times in the week given

    Each dictionary in the returned list contains:
      - name (str): The name or identifier
      - mfy_total (int): The total value
      - mfy_count (int): The number of items counted
      - mfy_average (int): The average value
    
    This function will return:
      - True/False, if the function passed
      - String Message, displays what caused the function to fail
      - Dictionary, list of the mfy data, will be empty if failed.

    @param date: The week ending date string in the format 'YY-MM-DD'.
    """
    roster = getRosterFromDate(date)
    if roster == False:
        return False, "roster_calc", []
    
    try:
        total_mfy_data = createTemplateData(roster)
        # Start main Algorithm

        for i in range(0, len(roster)):
            mfy = getMFYFromDate(roster[i]["date"], date)
            if mfy == False or mfy == []:
                return False, "mfy_calc", []
            for j in range(0, len(mfy)):
                workersInHour = checkWorkersInHour(roster, i, mfy, j)
                if workersInHour == False:
                    return False, "workersinhour", []
                for k in range(0, len(roster[i]["data"])):
                    if (int(roster[i]["data"][k]["start"]) <= int(mfy[j]["start"])) and (int(roster[i]["data"][k]["end"]) >= int(mfy[j]["end"])):
                        if workersInHour[0] > 2:
                            if roster[i]["data"][k]["name"] != workersInHour[1] and roster[i]["data"][k]["name"] != workersInHour[2]:
                                continue
                        for l in range(0,len(total_mfy_data)):
                            if (roster[i]["data"][k]["name"] == total_mfy_data[l]["name"]):
                                total_mfy_data[l]["mfy_total"] += int(mfy[j]["MFY"])
                                total_mfy_data[l]["mfy_count"] += 1

        pop_indexs = []
        for i in range(0, len(total_mfy_data)):
            if total_mfy_data[i]["mfy_total"] == 0 or total_mfy_data[i]["mfy_count"] == 0:
                pop_indexs.append(i)
            else:
                total_mfy_data[i]["mfy_average"] = round(total_mfy_data[i]["mfy_total"] / total_mfy_data[i]["mfy_count"])
                
        for i in range(len(pop_indexs)):
            total_mfy_data.pop(pop_indexs[i] - i)

        total_mfy_data = sortByAverage(total_mfy_data)
    
        return True, "", total_mfy_data
    except:
        return False, "calculation", []

def print_data(total_mfy_data: list[dict[str, int]]):
    print("\nRankings:")
    for i in range(0, len(total_mfy_data)):
        print(f"{i+1}.\t{total_mfy_data[i]["name"]}: {total_mfy_data[i]["mfy_average"]}")



if __name__ == "__main__":
    date = input("Please enter week ending date to generate MFY averages, e.g(25-03-16):\n")

    data_folder_list = os.listdir('data')
    found = False
    for i in range(0, len(data_folder_list)):
        if data_folder_list[i] == date:
            found = True
            print("Date Found")

    if not found:
        print("Date Not Found")
        quit()

    passed, message, total_mfy_data = calculate_data(date)

    if passed:
        print_data(total_mfy_data)
    else:
        print(message)












