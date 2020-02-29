class Session:
    def __init__(self):
        self.id = 0
        self.description = ''
        self.name = ''
        self.username = ''
        self.terminateAt = ''
        self.userId = 0
        self.screenName = ''
        self.active = False
        self.notificationEnabled = False
        self.createdAt = ''
        self.friendlyName = ''
        self.hashesInFile = 0
        self.hashFileExists = False
        self.validation = None
        self.guessHashType = ''
        self.hashcat = None
