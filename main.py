import os
import json

### TODO: Make it only accept the 2 best ppl on line for the score
### TODO: Round every score under 30 into 30
### TODO: Organise code :D
### TODO: show jake and adam

def getRosterFromDate(date: str):
    f = open(f'data/{date}/roster.json', "r")
    roster_data = json.loads(f.read())
    f.close()
    return roster_data

def getMFYFromDate(date: str):
    mfyData = date.split('-')
    f = open(f'data/{DATE}/{mfyData[2]}-MFY.json', "r")
    mfyData = json.loads(f.read())
    f.close()
    return mfyData

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


DATE = input("Please enter week ending date to generate MFY averages, e.g(25-3-16):\n")

data_folder_list = os.listdir('data')
found = False
for i in range(0, len(data_folder_list)):
    if data_folder_list[i] == DATE:
        found = True
        print("Date Found")

if not found:
    print("Date Not Found")
    quit()

# Create Roster list with unique names and 0 MFY time
roster = getRosterFromDate(DATE)
total_mfy_data = []
for i in range(0, len(roster)):
    for j in range(0, len(roster[i]["data"])):
        nameInData = False
        for k in range(0, len(total_mfy_data)):
            if roster[i]["data"][j]["name"] == total_mfy_data[k]["name"]:
                nameInData = True
        if nameInData == False:
            total_mfy_data.append({
                "name": roster[i]["data"][j]["name"],
                "mfy_total": 0,
                "mfy_count": 0,
                "mfy_average": 0})


# Start main Algorithm
for i in range(0, len(roster)):
    print(roster[i]["date"])
    mfy = getMFYFromDate(roster[i]["date"])
    for j in range(0, len(mfy)):
        print(mfy[j])
        for k in range(0, len(roster[i]["data"])):
            
            #print(roster[i]["data"][k]["start"], mfy[j]["start"], (int(roster[i]["data"][k]["start"]) <= int(mfy[j]["start"])) and (int(roster[i]["data"][k]["end"]) >= int(mfy[j]["end"])))
            if (int(roster[i]["data"][k]["start"]) <= int(mfy[j]["start"])) and (int(roster[i]["data"][k]["end"]) >= int(mfy[j]["end"])):
                if (roster[i]["data"][k]["name"] == "Max Kershaw"):
                    print("Max Kershaw ^")
                for l in range(0,len(total_mfy_data)):
                    if (roster[i]["data"][k]["name"] == total_mfy_data[l]["name"]):
                        total_mfy_data[l]["mfy_total"] += int(mfy[j]["MFY"])
                        total_mfy_data[l]["mfy_count"] += 1

    print("\n")


for i in range(0, len(total_mfy_data)):
    total_mfy_data[i]["mfy_average"] = total_mfy_data[i]["mfy_total"] / total_mfy_data[i]["mfy_count"]

total_mfy_data = sortByAverage(total_mfy_data)

print(total_mfy_data)

for i in range(0, len(total_mfy_data)):
    print(f"{total_mfy_data[i]["name"]}: {total_mfy_data[i]["mfy_average"]}")