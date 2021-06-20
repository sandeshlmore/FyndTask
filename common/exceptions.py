

class APIError(Exception):
    def __init__(self, error_code, error_message, traceback):
        self.error_code = error_code or ''  # Error Codes have not been defined yet.
        self.error_message = str(error_message)
        self.traceback = traceback

    def make_error_response(self):
        # return [{'error_code': self.error_code, 'message': self.error_message, 'traceback': self.traceback}]
        return [{'message': self.error_message, 'traceback': self.traceback}]