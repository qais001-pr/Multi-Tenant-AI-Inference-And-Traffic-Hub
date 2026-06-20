from pydantic import BaseModel #type: ignore
class Emails(BaseModel):
    email: str