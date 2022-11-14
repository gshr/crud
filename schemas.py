from pydantic import BaseModel
from typing import Optional


class UserInfo(BaseModel):
    #ADDHAR_ID: Optional[str] = None
    NAME: str
    ADDRESS: str
    AGE: int
    COUNTRY: str
