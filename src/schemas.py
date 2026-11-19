from pydantic import BaseModel, Field


class AuthTokenResponse(BaseModel):
    token: str = Field(..., min_length=8)


class BookingDates(BaseModel):
    checkin: str
    checkout: str


class BookingPayload(BaseModel):
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    totalprice: int = Field(..., ge=0)
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str = ""


class BookingRecord(BaseModel):
    bookingid: int
    booking: BookingPayload


class HealthResponse(BaseModel):
    status: str
    service: str
