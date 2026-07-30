import datetime

def add_business_days(start_date, days_to_add, holidays=None):
    """
    Adds business days (Mon-Fri) to a date, skipping provided holidays.
    start_date: datetime.date object
    days_to_add: int
    holidays: list of YYYY-MM-DD strings
    """
    if holidays is None:
        holidays = []
    
    # Convert string holidays to date objects
    holiday_set = set()
    for h in holidays:
        try:
            holiday_set.add(datetime.datetime.strptime(h, '%Y-%m-%d').date())
        except ValueError:
            continue

    current_date = start_date
    added_days = 0
    
    while added_days < days_to_add:
        current_date += datetime.timedelta(days=1)
        # Skip weekends (5=Sat, 6=Sun) and holidays
        if current_date.weekday() < 5 and current_date not in holiday_set:
            added_days += 1
            
    return current_date

def main():
    # Example: Calculate a deadline 10 business days from now
    start = datetime.date.today()
    office_holidays = ['2026-08-03', '2026-09-07']
    
    deadline = add_business_days(start, 10, office_holidays)
    
    print(f"Start date: {start}")
    print(f"Deadline after 10 business days: {deadline}")

if __name__ == '__main__':
    main()
