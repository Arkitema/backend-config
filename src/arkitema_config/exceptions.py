class DatabaseItemNotFound(Exception):
    pass


class AuthenticationError(LookupError):
    pass


class MicroServiceConnectionError(ConnectionError):
    pass


class MicroServiceResponseError(Exception):
    pass


class MSGraphException(Exception):
    pass
