import os

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def get_next_date(last_date: str) -> str:
    """
    Returns the date 7 days after the date given.

    @param last_date: A date string in the format 'YY-MM-DD'.
    @return: The date 7 days after last_date as a string in the format 'YY-MM-DD'.
    """
    [year, month, day] = last_date.split('-')
    year, month, day = int(year), int(month), int(day)
    day += 7
    if day > days_in_month[month-1]:
        day -= days_in_month[month-1]
        month += 1
    if month > 12:
        month = 1
        year += 1
    return f"{year:02}-{month:02}-{day:02}"

if __name__ == "__main__":
    list = os.listdir('data')
    print(list)
    os.makedirs(f"data/{get_next_date(list[-1])}")
