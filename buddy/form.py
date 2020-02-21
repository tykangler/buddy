import datetime

class Formatter:
   def __init__(self):
      pass

def fill_date(today, year, month, day):
   MILLE = 1000
   CENTURY = 100
   millenium = today.year // MILLE * MILLE
   if year <= today.year % millenium:
      year += millenium
   elif year < CENTURY:
      year += millenium - CENTURY
   return datetime.date(year, month, day)

def parse_date(date_str: str, delim="-"):
   """
   possible formats:
   -----------------------------
   day -> 2, 3, 10, 2
   month-day -> 12-2, 6-7, 2-09
   month-day-year -> 12-2-2000, 7-18-1998, 2-9-2020
   month-day-year -> 12-2-00, 7-18-98, 2-9-20
   
   ommitted terms assumed to be current
   delim represents separator between date terms
   if delim not specified, then default is '-'

   Can specify how many days back with 'Nd' or 'ND' where 
   N represents the number of days before today
   """
   today = datetime.date.today()
   if not date_str:
      return today
   elif len(date_str) == 2 and date_str[1].lower() == 'd':
      year, month, day = today.year, today.month, today.day - int(date_str[0])
      return datetime.date(year, month, day)
   else:
      date_list = [int(elem) for elem in date_str.split(delim)]
      if len(date_list) == 2:
         date_list[0], date_list[1] = date_list[1], date_list[0] 
         # month, day = day, month
      unpack_date = lambda day=today.day, month=today.month, year=today.year: (year, month, day)
      year, month, day = unpack_date(*date_list)
      return fill_date(today, year, month, day)

