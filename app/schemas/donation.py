from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = Field(None)

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class DonationMyRead(DonationBase):
    id: int
    create_date: dt

    class Config:
        orm_mode = True


class DonationDB(DonationBase):
    id: int
    create_date: dt
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[dt] = Field(None)

    class Config:
        orm_mode = True
