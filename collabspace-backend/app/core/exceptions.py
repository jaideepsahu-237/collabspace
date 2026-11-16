class AppException(Exception):
    def __init__(self, message : str, status_code : int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class TenantNotFoundException(AppException):

    def __init__(self, tenant_id : int):
        super().__init__(
            message=f"Tenant with ID {tenant_id} not found",
            status_code=404
        )

class UserAlreadyExistsException(AppException):

    def __init__(self, email : str):
        super().__init__(
            message="Email already registered",
            status_code=409
        )

class InvalidCredentialsException(AppException):

    def __init__(self):
        super().__init__(message="Invalid email or password", status_code=401)

class InvalidTokenException(AppException):

    def __init__(self):
        super().__init__(message="Could not validate credentials", status_code=401)