from pydantic import BaseModel, model_validator
from datetime import date, datetime

class ScheduleBase(BaseModel):
    guest_id: int
    event_id: int
    room_id: int
    date: date
    start_time: datetime
    end_time: datetime

    @model_validator(mode='after')
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.start_time.date() != self.date:
            raise ValueError("start_time date must match the date field")
        return self


class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    schedule_id: int