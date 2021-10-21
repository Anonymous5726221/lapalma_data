from datetime import datetime as dt

# After init they can only be changed through callbacks, be mindful of that
def get_date_picker_settings():
    start_date = dt(2021,8,4).date()
    end_date = dt.now().date()
    display_fmt = "YYYY/MM/DD"
    return start_date, end_date, display_fmt
