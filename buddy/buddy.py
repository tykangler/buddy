from pathlib import Path
import os
import balance
import argparse
import json
import datetime
import form

INTRO = "Hi I'm Buddy!"

def main():
   income_file = os.path.join(Path.home(), r"buddy\income.json")
   expense_file = os.path.join(Path.home(), r"buddy\expense.json")
   prompt = "No {0} found, add planned {0} (y/n)? "
   parser = def_args()
   arguments = parser.parse_args()

   income_balance = retrieve_balance(income_file, prompt.format("income"))
   expense_balance = retrieve_balance(expense_file, prompt.format("expenses"))

def def_args():
   parser = argparse.ArgumentParser(description=INTRO)
   subparsers = parser.add_subparsers()
   access_parser = argparse.ArgumentParser(add_help=False)
   access_parser.add_argument("id", type=int)

   transaction_parser = argparse.ArgumentParser(add_help=False)
   transaction_parser.add_argument("name")
   transaction_parser.add_argument("amount", type=balance.Money)
   transaction_parser.add_argument("--date", "-d") # assume to be now
   transaction_parser.add_argument("--category", "-c")

   view_parser = subparsers.add_parser("view", help="view budget plan")
   view_parser.add_argument("what", choices={"planned", "actual", "all"}, nargs="?", default="all")

   add_parser = subparsers.add_parser("add", help="add cashflow categories to the budget plan")
   add_parser.add_argument("--income", "-i", nargs="*", action=SeqToDict)
   add_parser.add_argument("--expense", "-e", nargs="*", action=SeqToDict)

   subparsers.add_parser("remove", help="remove cashflow categories from the budget plan",
                         parents=[access_parser])
   edit_parser= subparsers.add_parser("edit", help="edit groups or transactions", 
                         parents=[access_parser])
   edit_parser.add_argument("--name", "-n")
   edit_parser.add_argument("--amount", "-a")
   edit_parser.add_argument("--date", "-d") # condition for groups and transactions

   subparsers.add_parser("spend", help="spend some money", parents=[transaction_parser])
   subparsers.add_parser("earn", help="add income", parents=[transaction_parser])
   return parser

class SeqToDict(argparse.Action):
   def __call__(self, parser, namespace, values, option_string=None):
      d = dict(zip(*[iter(values)] * 2))
      setattr(namespace, self.dest, {key: balance.Money(d[key]) for key in d})

def retrieve_balance(file_path, prompt):
   """
   searches file_path for balance data. if file is not found, then prompts
   user to add planned amounts.
   returns a dictionary of categories to category data
   """
   if os.path.isfile(file_path):
      with open(file_path) as data:
         budget_data = json.load(data, object_hook=balance.Budget.from_json)
   else:
      if input(prompt) == 'y':
         pass # TODO implement
      else:
         budget_data = {}
   return budget_data

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
   -----------------------------
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

if __name__ == "__main__":
   main()