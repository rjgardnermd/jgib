import traceback
from datetime import datetime


def exceptionToStr(e: Exception) -> str:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = f"Exception was thrown at {current_time}:\n{''.join(traceback.format_exception(None, e, e.__traceback__))}"
    return error_message
