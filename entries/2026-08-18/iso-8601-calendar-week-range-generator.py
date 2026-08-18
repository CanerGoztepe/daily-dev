import datetime

def get_week_range(year, week_number):
    """
    Calculates the start and end dates (Monday to Sunday) for an ISO week.
    Returns a tuple of (start_date, end_date).
    """
    try:
        # ISO weeks start from 1, years have 52 or 53 weeks.
        if not (1 <= week_number <= 53):
            raise ValueError("Week number must be between 1 and 53.")
        
        # Create a date object for the first day of the year
        first_day_of_year = datetime.date(year, 1, 1)
        
        # Find the first Monday of the year
        days_to_monday = (7 - first_day_of_year.weekday()) % 7
        first_monday = first_day_of_year + datetime.timedelta(days=days_to_monday)
        
        # Calculate the start of the target week
        # Offset by (week_number - 1) weeks
        start_date = first_monday + datetime.timedelta(weeks=week_number - 1)
        
        # End date is 6 days after start
        end_date = start_date + datetime.timedelta(days=6)
        
        return start_date, end_date
    except ValueError as e:
        return f"Calculation error: {e}"

def main():
    # Example: Get range for the 10th week of 2026
    year = 2026
    week = 10
    result = get_week_range(year, week)
    
    if isinstance(result, tuple):
        start, end = result
        print(f"Year: {year}, Week: {week}")
        print(f"Start (Monday): {start.isoformat()}")
        print(f"End (Sunday): {end.isoformat()}")
    else:
        print(result)

if __name__ == '__main__':
    main()
