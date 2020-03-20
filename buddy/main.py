import argparse
import datetime
import decimal
import json
import os
from pathlib import Path
import re
from numbers import Number

import budget
import form
import ledger
import linker

INTRO = "Hi {0}! I'm Buddy!"
DEFAULT_DATE = (datetime.date.today(), 
                datetime.date.today() + datetime.timedelta(days=30))

# files
data_dir = os.path.join(Path.home(), "buddy")
budget_path = os.path.join(data_dir, "budget.json")
ledger_path = os.path.join(data_dir, "ledger.json")
user_path = os.path.join(data_dir, "user.json")
linker_path = os.path.join(data_dir, "relationships.json")

SECTIONS = ["income", "expense"]

def main():
   # retrieve user data
   save_data = retrieve_data(user_path)

   # parse arguments
   parser = define_parser(save_data)
   args = parser.parse_args()
   args.func(args, save_data)

def define_parser(save_data):
   parser = argparse.ArgumentParser(description=INTRO.format(save_data["name"]))
   subparsers = parser.add_subparsers(dest="command")

   # parents -----------------------------
   use_regex_parser = argparse.ArgumentParser(add_help=False)
   use_regex_parser.add_argument("--use-regex", "-r", action="store_true", default=save_data["use_regex"])

   use_id_parser = argparse.ArgumentParser(add_help=False)
   use_id_parser.add_argument("--use-id", "-i", action="store_true", default=save_data["use_id"])

   # report ------------------------------
   # report_parser = subparsers.add_parser("report", help="report budget plan")
   # report_parser.set_defaults(func=view_handle)

   # create ------------------------------
   create_parser = subparsers.add_parser("create", help="create a budget with date range",
                                         parents=[use_regex_parser, use_id_parser])
   create_parser.add_argument("--only", help="create only budget or only ledger", 
                              choices={"budget", "b", "ledger", "l"}, nargs="*")
   create_parser.add_argument("--name")
   create_parser.add_argument("--from", type=parse_date, dest="from_date", 
                              default=datetime.date.today())
   create_parser.add_argument("--to", type=parse_date, dest="to_date")
   create_parser.add_argument("--link")

   # plan --------------------------------
   plan_parser = subparsers.add_parser("plan", help="plan cashflows for budget",
                                       parents=[use_regex_parser, use_id_parser])
   plan_parser.add_argument("--budget", "-b")
   plan_parser.add_argument("section", choices={"income", "i", "expense", "e"})
   plan_parser.add_argument("entries", nargs="*", action=SeqToDict)
   plan_parser.set_defaults(func=plan_handle)

   # remove ------------------------------
   remove_parser = subparsers.add_parser("remove", 
                                         help="remove cashflow categories from the budget plan",
                                         parents=[use_regex_parser, use_id_parser])
   remove_parser.add_argument("--budget", "-b")
   remove_parser.add_argument("--ledger", "-l")
   remove_parser.add_argument("--transaction", "-t")
   remove_parser.add_argument("--planned", "-p")
   remove_parser.set_defaults(func=remove_handle)

   # edit -------------------------------
   edit_parser = subparsers.add_parser("edit", help="edit groups or transactions",
                                       parents=[use_regex_parser, use_id_parser])
   edit_parser.add_argument("--name")
   edit_parser.add_argument("--amount", type=decimal.Decimal)
   edit_parser.add_argument("--from", dest="from_date", type=parse_date)
   edit_parser.add_argument("--to", dest="to_date", type=parse_date)
   edit_parser.add_argument("--date", type=parse_date)
   edit_parser.add_argument("--group")
   edit_parser.add_argument("--link")
   edit_parser.add_argument("--budget", "-b")
   edit_parser.add_argument("--ledger", "-l")
   edit_parser.add_argument("--transaction", "-t")
   edit_parser.add_argument("--planned", "-p")
   edit_parser.set_defaults(func=edit_handle)

   # spend ------------------------------
   spend_parser = subparsers.add_parser("spend", help="spend some money",
                                        parents=[use_regex_parser, use_id_parser])
   spend_parser.add_argument("--budget", "-b")
   spend_parser.add_argument("--ledger", "-l")
   spend_parser.add_argument("--group")
   spend_parser.add_argument("name")
   spend_parser.add_argument("amount", type=decimal.Decimal)
   spend_parser.add_argument("date", type=parse_date, default=datetime.date.today())

   # earn -------------------------------
   earn_parser = subparsers.add_parser("earn", help="add income",
                                       parents=[use_regex_parser, use_id_parser])
   earn_parser.add_argument("--budget", "-b")
   earn_parser.add_argument("--ledger", "-l")
   earn_parser.add_argument("--group")
   earn_parser.add_argument("name")
   earn_parser.add_argument("amount", type=decimal.Decimal)
   earn_parser.add_argument("date", type=parse_date, default=datetime.date.today())

   return parser

# --------------------------
# date parsing
# --------------------------

# region

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

   Can specify how many days, weeks, months back with 'Nd' or 'ND' where 
   N represents the number of days after today.

   Replace 'd' with 'w' or 'm' to specify weeks or months. Months will be
   interpreted as 4 weeks as per pay schedule

   if date_str is false, then return today 
   """
   today = datetime.date.today()
   if not date_str:
      return today
   elif len(date_str) == 2:
      date_spec = {"d": datetime.timedelta(days=int(date_str[0])),
                   "w": datetime.timedelta(weeks=int(date_str[0])),
                   "m": datetime.timedelta(weeks=4 * int(date_str[0]))}
      return today + date_spec[date_str[0].lower()]
   else:
      date_list = [int(elem) for elem in date_str.split(delim)]
      if len(date_list) >= 2:
         date_list[0], date_list[1] = date_list[1], date_list[0] 
         # month, day = day, month
      unpack_date = lambda day=today.day, month=today.month, year=today.year: (year, month, day)
      year, month, day = unpack_date(*date_list)
      return fill_date(today, year, month, day)

# endregion

# --------------------------
# Misc and Errors
# --------------------------

# region

class SeqToDict(argparse.Action):
   def __call__(self, parser, namespace, values, option_string=None):
      d = dict(zip(*[iter(values)] * 2))
      setattr(namespace, self.dest, {key: decimal.Decimal(d[key]) for key in d})

class DataNotFoundError(Exception):
   def __init__(self, msg):
      self.msg = msg

class IncompleteSpecError(Exception):
   def __init__(self, msg):
      self.msg = msg

class NotInitializedError(Exception):
   def __init__(self, msg):
      self.msg = msg

# endregion

# ----------------------
# choice parsing
# ----------------------

# region 

def parse_choice(iterable, pattern: str, *, regex=False, key=str, print_out=str):
   """
   takes an iterable with mappings from an integer id to an object, and returns an id value
   whose mapping matches the given pattern. If multiple options are found, then the options
   are printed, allowing the user to choose one according to their id. 
   <iterable> must support __getitem__ and __iter__, and iterate over a set of integer ids. 
   <regex> is a boolean designating whether to use regex to match strings, <key> is a 
   function returning a string used to match a mapped object to the given pattern. 
   <print_out> is a function returning a string specifying what should be printed out. 
   """
   options = possible_options(iterable, pattern, regex=regex, key=key)
   if options:
      if len(options) > 1:
         print_options(options, iterable, print_out=print_out)
         user_choice = retrieve_user_choice(options)
      else:
         user_choice = 0
      return options[user_choice]
   return None

def possible_options(iterable, pattern, *, regex, key):
   if not regex:
      matches = [i for i in iterable if pattern in key(iterable[i])]
   else:
      matches = [i for i in iterable if re.search(pattern, key(iterable[i]))]
   return matches
   
def print_options(options, iterable, print_out):
   print(f"{len(options)} options found")
   print("-------------------------")
   for i in range(len(options)):
      print(str(i) + ". " + print_out(iterable[options[i]]))

def retrieve_user_choice(options):
   user_choice = input("Choose: ")
   if not user_choice.isdigit():
      raise ValueError("Not Valid Choice")
   user_choice = int(user_choice)
   if user_choice not in options:
      raise ValueError("Not Valid Choice")
   return user_choice

# endregion

# ---------------------------
# json and file handling
# ---------------------------

# region

def json_to_obj_budgets(obj):
   return {entry_id: budget.Budget.from_json(obj[entry_id]) for entry_id in obj}

def obj_to_json_budgets(obj):
   return {entry_id: obj[entry_id].to_json() for entry_id in obj}

def json_to_obj_ledgers(obj):
   return {entry_id: ledger.Ledger.from_json(obj[entry_id]) for entry_id in obj}

def obj_to_json_ledgers(obj):
   return {entry_id: obj[entry_id].to_json() for entry_id in obj}

def retrieve_data(path, *, hook=None):
   if os.path.isfile(path):
      with open(path, "r") as file_input:
         return json.load(file_input, object_hook=hook)
   return None

def write_data(obj, path, *, hook=None):
   with open(path, "w") as file_output:
      json.dump(obj, file_output, default=hook)

# endregion

# ---------------------
# action handlers
# ---------------------

# region

# helpers -------------



# create --------------

def create_and_write_budget(args, new_budget_id, budgets, to_date):
   name = args.name or f"Budget {new_budget_id}"
   budgets[new_budget_id] = budget.Budget(name, args.from_date, to_date)
   write_data(budgets, budget_path, hook=obj_to_json_budgets)

def create_and_write_ledger(args, new_ledger_id, ledgers, to_date):
   name = args.name or f"Ledger {new_ledger_id}"
   ledgers[new_ledger_id] = ledger.Ledger(name, args.from_date, to_date)
   write_data(ledgers, ledger_path, hook=obj_to_json_ledgers)

def create_handle(args, save_data):
   links = retrieve_data(linker_path, hook=linker.Linker.from_json)
   budgets = retrieve_data(budget_path, hook=json_to_obj_budgets) or dict()
   ledgers = retrieve_data(ledger_path, hook=json_to_obj_ledgers) or dict()
   to_date = args.to_date or args.from_date + datetime.timedelta(weeks=4)

   if args.only == "budget":
      save_data["last_budget"] += 1
      new_budget_id = save_data["last_budget"]
      create_and_write_budget(args, new_budget_id, budgets, to_date)
      if args.link:
         ledger_link = (args.link if args.use_id 
            else parse_choice(ledgers, args.link, regex=args.use_regex))
         if not ledger_link or ledger_link not in ledgers:
            raise DataNotFoundError(f"ledger with id {ledger_link} not found")
         links.create_link(new_budget_id, ledger_link)

   elif args.only == "ledger":
      save_data["last_ledger"] += 1
      new_ledger_id = save_data["last_ledger"]
      create_and_write_ledger(args, new_ledger_id, ledgers, to_date)
      if args.link:
         budget_link = (args.link if args.use_id 
            else parse_choice(budgets, args.link, regex=args.use_regex))
         if not budget_link or budget_link not in budgets:
            raise DataNotFoundError(f"budget with id {budget_link} not found")
         links.create_link(budget_link, new_ledger_id)

   else:
      save_data["last_budget"] += 1
      new_budget_id = save_data["last_budget"]
      create_and_write_budget(args, new_budget_id, budgets, to_date)

      save_data["last_ledger"] += 1
      new_ledger_id = save_data["last_ledger"]
      create_and_write_ledger(args, new_ledger_id, ledgers, to_date)

      links.create_link(new_budget_id, new_ledger_id)

   write_data(links, linker_path, hook=linker.Linker.to_json)

# plan -------------------------- TODO error checking

def plan_handle(args, save_data): 
   def add_entries_from_dict(budget_sec, save_data):
      for entry_name in args.entries:
         save_data["last_planned"] += 1
         budget_sec.add(save_data["last_planned"], entry_name, args.entries[entry_name])
   budgets = retrieve_data(budget_path, hook=json_to_obj_budgets)
   if not budgets:
      raise NotInitializedError(f"no budgets have been created")
   target_budget_id = (args.budget if args.use_id 
      else parse_choice(budgets, args.budget, regex=args.use_regex))
   target_budget = budgets[target_budget_id]
   if args.section == "income" or args.section == "i":
      add_entries_from_dict(target_budget.income(), save_data)
   elif args.section == "expense" or args.section == "e":
      add_entries_from_dict(target_budget.expense(), save_data)

# remove -------------------------

def remove_handle(args, save_data): 
   budgets = retrieve_data(budget_path, hook=json_to_obj_budgets)
   ledgers = retrieve_data(ledger_path, hook=json_to_obj_ledgers)
   # remove transaction ----------
   if args.transaction:
      if not args.ledger:
         raise IncompleteSpecError(f"can't find transaction {args.transaction} without ledger")
      if not ledgers:
         raise NotInitializedError("no ledgers created")
      ledger_id = (args.ledger if args.use_id 
                   else parse_choice(ledgers, args.ledger, regex=args.use_regex))
      if not ledger_id or ledger_id not in ledgers:
         raise DataNotFoundError(f"ledger {args.ledger} not found")
      transaction_id = (args.transaction if args.use_id else 
                        parse_choice(ledgers[ledger_id], args.transaction, regex=args.use_regex))
      if not transaction_id or transaction_id not in ledgers[ledger_id]:
         raise DataNotFoundError(f"transaction {args.transaction} not found")
      ledgers[ledger_id].remove(transaction_id)
   # remove budget entry ------------------
   elif args.planned:
      if not args.budget:
         raise IncompleteSpecError(f"can't find entry {args.planned} without budget")
      if not budgets:
         raise NotInitializedError("no budgets created")
      budget_id = (args.budget if args.use_id
                   else parse_choice(budgets, args.budget, regex=args.use_regex))
      if not budget_id or budget_id not in budgets:
         raise DataNotFoundError(f"budget {args.budget} not found")
      planned_id = (args.planned if args.use_id else 
                    parse_choice(budgets[budget_id], args.planned, regex=args.use_regex,
                                 key=lambda entry: entry[1].name, 
                                 print_out=lambda entry: f"{entry[1].name} {entry[0]}"))
      if not planned_id or planned_id not in budgets[budget_id]:
         raise DataNotFoundError(f"planned entry {args.planned} not found")
      budgets[budget_id].section(planned_id).remove(planned_id)
   # remove ledger -------------------
   elif args.ledger:
      if not ledgers:
         raise NotInitializedError("no ledgers created")
      ledger_id = (args.ledger if args.use_id
                   else parse_choice(ledgers, args.ledger, regex=args.use_regex))
      if not ledger_id or ledger_id not in ledgers:
         raise DataNotFoundError(f"ledger {args.ledger} not found")
      del ledgers[ledger_id]
   # remove budget ---------------------
   elif args.budget:
      if not budgets:
         raise NotInitializedError("no budgets created")
      budget_id = (args.budget if args.use_id
                   else parse_choice(budgets, args.budger, regex=args.use_regex))
      if not budget_id or budget_id not in budgets:
         raise DataNotFoundError(f"budget {args.budget} not found")
      del budgets[budget_id]
   
   else:
      raise IncompleteSpecError(f"nothing to remove specified")
      
def edit_handle(args, save_data): # edit links
   pass

def transaction_handle(args, save_data):
   pass
   
# endregion

# ---------------------
# END
# ---------------------

if __name__ == "__main__":
   main()
