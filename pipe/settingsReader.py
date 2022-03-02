
import sys

class Settings:
    def __init__(self, pathToSettingsDirectory):
        self.pathToSettings = pathToSettingsDirectory
        if not self.pathToSettings in sys.path:
            sys.path.append(self.pathToSettings)
        import settings
        self.settings = settings

    def __getitem__(self, key):
        return self.settings.__getattribute__(key)
