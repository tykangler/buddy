import datetime as dt
import math
from decimal import Decimal

class ScheduleError(Exception):
   pass

def __calc_schedule_periods(start: dt.date, last: dt.date, perlen: dt.timedelta) -> int:
   if not start or not last or not perlen:
      raise ScheduleError("can't calculate schedule periods without start, last, or period length")
   delta = last - start
   return math.ceil(delta / perlen)

class Schedule:
   def __init__(self, account, start, *, 
                last: dt.date=None, periods: int=None, perlen: dt.timedelta=None):
      if [last, periods, perlen].count(None) != 1:
         raise ScheduleError("only 2 of arguments (last, periods, and perlen) can be set")
      elif not start:
         raise ScheduleError("can't create schedule without a start date")
      self.start = start
      self._account = account
      if last and periods:
         perlen = (last - start) / periods
      elif periods and perlen:
         last = start + periods * perlen
      else:
         periods = __calc_schedule_periods(start, last, perlen)
      self._schedule = {start + perlen * per: Decimal(0) for per in range(1, periods + 1)}

   def __iter__(self):
      return iter(self._schedule)

   def __getitem__(self, date):
      return self._schedule[date]

   def __setitem__(self, date, amount):
      if date not in self._schedule:
         raise ScheduleError(f"{date} not a valid date in schedule")
      self._schedule[date] = amount

   def iloc(self, period):
      if period > len(self._schedule) or period <= 0:
         raise ScheduleError(f"{period} not within range of periods")
      return self._schedule[list(self._schedule)[period - 1]]

   def recur(self, amount):
      for date in self._schedule:
         self._schedule[date] = Decimal(amount)

   def straight(self, start_balance, end_balance):
      recurring_amt = (end_balance - start_balance) / len(self._schedule)
      self.recur(recurring_amt)