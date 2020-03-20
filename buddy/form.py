from datetime import date, timedelta
import math
import re
from itertools import chain

def with_pad(text, *, pad=" "):
   return pad + text + pad

def print_hdivider(widths):
   print(with_pad("-" * widths[0], pad="-"), end="")
   for i in range(1, len(widths)):
      print("+", end="")
      print(with_pad("-" * widths[i], pad="-"), end="")
   print()

def print_row(items):
   "items is a list of iterables (text, align, width): [(item, align, width)*]"
   TEXT, ALIGN, WIDTH = 0, 1, 2
   align_and_pad = lambda text, align, width: with_pad(f"{text: {align}{width}}")
   first = items[0]
   print(align_and_pad(first[TEXT], first[ALIGN], first[WIDTH]), end="")
   for i in range(1, len(items)):
      item = items[i]
      print("|", end="")
      print(align_and_pad(item[TEXT], item[ALIGN], item[WIDTH]), end="")
   print()

def print_date_range(date_format, from_date: date, to_date: date):
   print((f"From {from_date.strftime(date_format)} "
            f"to {to_date.strftime(date_format)}"))

def width_int(val: int):
   return int(math.log10(abs(val))) // 1 + 1 if val >= 10 else 1

def width_money(val, *, precision=2, sign=False):
   "sign will be True for negative numbers regardless of the sign variable"
   width = (1 if sign or val < 0 else 0) + 2 + precision # +2 for "1."
   # val >= 10 because all values under 10 will have 0 additional digits
   abs_val = abs(val)
   additional_digits = int(math.log10(abs_val)) // 1 if abs_val >= 10 else 0
   return width + additional_digits

class View:
   VALUE_WIDTH = 4
   VALUE_CHANGE_WIDTH = 5 # (+0.00)
   WIDTH_DATE = 8
   DATE_FORMAT = "%m/%d/%y"

   def __init__(self, args):
      pass

   def output(self):
      raise NotImplementedError

class TransactionView(View):
   WIDTH_NAME_COL = 35

   def output(self):
      pass

class GroupView(View):
   def output(self):
      pass
   
class PLView(GroupView, TransactionView):
   def output(self):
      pass

class SummaryView(View):
   def output(self):
      pass
