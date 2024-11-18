from pydantic import BaseModel


class Env(BaseModel):
    logDirectory: str
    logLevel: str
    internalApiUri: str
