from pydantic import BaseModel, constr


class SignUp(BaseModel):
    nickname: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=128)


class Login(BaseModel):
    nickname: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=128)
