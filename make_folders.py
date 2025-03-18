import os

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

start_date = [16, 3] # dd/mm
add_weeks = 1

def get_next_date(last_date: str) -> str:
    [year, month, day] = last_date.split('-')
    year, month, day = int(year), int(month), int(day)
    day += 7
    if day > days_in_month[month-1]:
        day -= days_in_month[month-1]
        month += 1
    if month > 12:
        month = 1
        year += 1
    return f"{year}-{month}-{day}"


list = os.listdir('data')
list.sort()
os.makedirs(f"data/{get_next_date(list[-1])}")
