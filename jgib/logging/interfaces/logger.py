from ..loggingConsts import LogLevel
from ...util import ensureDirExists


class Logger:
    def __init__(
        self,
        logDirectory: str,
        fileName: str,
        logLevel: LogLevel,
        printToConsole: bool = True,
    ):
        # Convert logLevel to enum if it's a string
        if isinstance(logLevel, str):
            try:
                logLevel = LogLevel[logLevel]
            except KeyError:
                raise ValueError(
                    f"Invalid log level: {logLevel}. Expected one of {list(LogLevel.__members__.keys())}"
                )

        elif not isinstance(logLevel, LogLevel):
            raise TypeError(
                f"logLevel must be an instance of LogLevel or a valid string, got {type(logLevel).__name__}"
            )

        ensureDirExists(logDirectory)
        self.filePath = f"{logDirectory}/{fileName}"
        self.logLevel: LogLevel = logLevel
        self.printToConsole: bool = printToConsole

    def clearLog(self):
        with open(self.filePath, "w") as file:
            pass
