import datetime
from typing import Union


def _format_array_values(array, formatter_func):
    """Helper function to format array values using a specified formatter.
    
    Args:
        array (list): Array of values to format
        formatter_func (callable): Formatter function to apply to each value
        
    Returns:
        list: List of formatted values
    """
    formatted_values = []
    for value in array:
        try:
            formatted = formatter_func(value)
            formatted_values.append(formatted if formatted is not None else value)
        except (TypeError, AttributeError):
            formatted_values.append(value)
    return formatted_values

def default(value: object):
    """Formatter functions handle Knack values by returning a formatted
    (aka, humanized) value.

    If the input value is a list, formats each element and returns them joined
    by commas. Otherwise returns the input value without additional formatting.
    """
    if isinstance(value, list):
        if not value or value == [None]:
            return None
        # Format each value in the array and join with commas
        formatted = [str(v) if v is not None else "" for v in value]
        return ", ".join(formatted)
    return value


def address(value: dict):
    """ return a string of comma-separated address elements, if present. 'latitude' and
    'longitude' keys are ignored. """
    keys = ["street", "street2", "city", "state", "zip", "country"]
    values = [value.get(key) for key in keys if value.get(key)]
    return ", ".join(values) if values else None


def multiple_choice(value: Union[list, str]):
    """ Handle a single string or list of strings """
    if isinstance(value, list):
        # account for this odd [None] value for empty multi-select fields
        if value == [None]:
            return None
        # we use string formatting to handle the possibility that the list contains ints
        return ", ".join([f"{val}" for val in value])
    return value


def signature(value: dict):
    return value.get("base30")


def email(value: dict):
    return value.get("email")


def link(value: dict):
    return value.get("url")


def phone(value: dict):
    return value.get("full")


def image(value):
    # somtimes a dict, sometimes a str
    try:
        return value["url"]
    except TypeError:
        return value


def file(value):
    # stack says it's ok to use `file` as a name:
    # https://stackoverflow.com/questions/24942358/is-file-a-keyword-in-python#:~:text=1%20Answer&text=It%20can%20be%20seen%20as,by%20the%20open()%20function. # noqa
    try:
        return value["url"]
    except TypeError:
        return value


def date_time(value, timezone=datetime.timezone.utc):
    """
    Given a unix timestamp and a timezone, return the timestamp in ISO format in local
    time with TZ offset str.

    Expecting a Knack datetime field value like so:
        ```
        "date_time": {
            "am_pm": "PM",
            "date": "09/11/2019",
            "date_formatted": "09/11/2019",
            "hours": "04",
            "iso_timestamp": "2019-09-11T16:14:00.000Z",
            "minutes": "14",
            "time": 974,
            "timestamp": "09/11/2019 04:14 pm",
            "unix_timestamp": 1568218440000,
        }
    ```
    """
    mills_timestamp = value.get("unix_timestamp")
    timestamp = mills_timestamp / 1000
    dt_utc = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    dt_local = dt_utc.astimezone(timezone)
    return dt_local.isoformat()


def timer(value):
    # we're handling somthing that looks like this:
    # '<span>09/11/19</span>&nbsp;4:14pm to 5:14pm = 1:00 hours'
    return value.replace("<span>", "").replace("</span>", "").replace("&nbsp;", "; ")


def connection(value):
    """
    Return a string of comma-separated values
    """
    if not value:
        return None
    else:
        # expecting a list of dicts like so:
        # [{'id': '5e7b63a0c279e606c645be7d', 'identifier': 'Some String'}]
        identifiers = [conn["identifier"] for conn in value]
        return ", ".join(str(v) for v in identifiers)
