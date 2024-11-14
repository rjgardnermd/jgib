from typing import List, Any
from tabulate import tabulate
from .loggingConsts import MAX_VALUE_LENGTH_IN_TABLES


def makeTable(
    data: List[List[str]],
    headers: List[str] = None,
    label: str = None,
    maxValueLength: int = MAX_VALUE_LENGTH_IN_TABLES,
) -> str:
    kwargs = {
        "tablefmt": "grid",
        "stralign": "left",
        "numalign": "left",
    }
    for row in data:
        for cellIdx, cellVal in enumerate(row):
            row[cellIdx] = truncateStr(cellVal, maxValueLength)
    if headers is None:
        table = tabulate(
            data,
            **kwargs,
        )
    else:
        table = tabulate(
            data,
            headers=headers,
            **kwargs,
        )
    s = "" if label is None else f"{label}:\n"
    return f"{s}{table}"


def truncateStr(s: Any, max_length: int) -> str:
    s = str(s)
    if len(s) > max_length - 3:
        return s[: max_length - 3] + "..."
    return s
