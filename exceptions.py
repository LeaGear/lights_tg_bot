


class ServiceError(Exception):
    """Base error business logic"""

class UnknownGroupError(ServiceError):
    pass
class UnknownProviderError(ServiceError):
    pass