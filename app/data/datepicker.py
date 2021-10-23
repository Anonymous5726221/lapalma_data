from datetime import datetime as dt


def get_date_picker_settings():
    start_date = dt(2021,8,4).date()
    end_date = dt.now().date()
    display_fmt = "YYYY/MM/DD"

    return {
        "start_date": start_date,
        "end_date": end_date,
        "display_format": display_fmt
    }