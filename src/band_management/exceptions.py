class BandManagementException(Exception):
    pass


class ValidationError(BandManagementException):
    pass


class PermissionDenied(BandManagementException):
    def __init__(self, *args, headers: dict = None, redirect: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        if not headers:
            headers = {}
        self.headers = headers
        self.redirect = redirect
