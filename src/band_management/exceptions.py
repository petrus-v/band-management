class BandManagementException(Exception):
    pass


class ValidationError(BandManagementException):
    pass


class PermissionDenied(BandManagementException):
    pass
