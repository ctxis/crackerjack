class Hashcat:
    def __init__(self):
        self.state = 0
        self.crackedPasswords = 0
        self.allPasswords = 0
        self.progress = 0
        self.timeRemaining = ''
        self.estimatedCompletionTime = ''
        self.dataRaw = ''
        self.data = ''
        self.incrementMin = 0
        self.incrementMax = 0
        self.incrementEnabled = False
        self.mode = 0
        self.hashType = ''
        self.wordlistType = 0
        self.wordlist = ''
        self.rule = ''
        self.mask = ''
        self.optimisedKernel = False
