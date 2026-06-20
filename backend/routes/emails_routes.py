from fastapi import APIRouter #type: ignore
from controller.email import add_user
from model.emailModel import Emails
emails_router = APIRouter()
@emails_router.post('/emails/add-user')
def store_email(data: Emails):
    print(data)
    print(data.email)
    return add_user(data.email)
    