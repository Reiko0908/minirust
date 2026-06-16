class ErrorToken(Exception):
    def __init__(self, s, line=None):
        self.message = "Error Token " + s
        self.line = line

class UncloseString(Exception):
    def __init__(self, s, line=None):
        self.message = "Unclosed String: " + s
        self.line = line

class IllegalEscape(Exception):
    def __init__(self, s, line=None):
        self.message = "Illegal Escape In String: " + s
        self.line = line
