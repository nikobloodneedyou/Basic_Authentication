from pydantic import BaseModel, EmailStr, field_validator


class UserCreateRequest(BaseModel):
    username: str | None = None
    user_code: str = ""
    email: EmailStr
    password: str
    age: int = 18
    role: str = "user"

    @field_validator("password")
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserCreateResponse(BaseModel):
    message: str


class UserProfileResponse(BaseModel):
    username: str
    user_code: str
    email: EmailStr
    age: int
    role: str


# Kept for backwards compatibility
class UserCreate(UserCreateRequest):
    pass


class UserResponse(UserProfileResponse):
    pass
