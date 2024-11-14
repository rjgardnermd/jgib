import os


def ensureDirExists(folderPath: str):
    if folderPath and not os.path.exists(folderPath):
        os.makedirs(folderPath)
