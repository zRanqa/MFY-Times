import os



days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

start_date = [13, 3] # dd/mm
end_date = [18, 3]   # dd/mm
# NOTE this program will create folders TO end_date - 1



curr_date = start_date
while curr_date != end_date:
    string = f"data/{start_date[0]}-{start_date[1]}"
    os.makedirs(string)
    # print(string)
    curr_date[0] += 1
    if curr_date[0] > days_in_month[curr_date[1] - 1]:
        curr_date[0] = 1
        curr_date[1] += 1