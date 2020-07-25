import datetime
from calendar import monthrange

# date specification:
# inputs:
# d, dd
# m/d, mm/dd
# yy/mm/dd
# yyyy/mm/dd
# (+/-)N(d/w/m/y)

DELIM = "/"
WEEKS_IN_MONTH = 4

def parse_date(date_str: str):
   today = datetime.date.today()
   date_parts = date_str.split(DELIM)
   if len(date_parts) == 1 and not date_parts[0].isdigit():
      dist, date_mult = int(date_parts[0][:-1]), date_parts[0][-1]
      date_dist = {'d': datetime.timedelta(days=dist),
                   'w': datetime.timedelta(weeks=dist),
                   'm': datetime.timedelta(weeks=dist * WEEKS_IN_MONTH),
                   'y': datetime.timedelta(years=dist)}[date_mult]
      return today + date_dist
   else:
      date_parts.reverse()
      unpack_date = (lambda day=today.day(), month=today.month(), year=today.year(): 
                       (day, month, year))
      day, month, year = unpack_date(*date_parts)
      return datetime.date(year, month, day)

def parse_dist(dist_str):
   pass