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
   create_parser.add_argument("--from", type=parse_date, dest="start", 
                              default=datetime.date.today())
   create_parser.add_argument("--to", type=parse_date, dest="end")
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
   edit_parser.add_argument("--name") # all
   edit_parser.add_argument("--amount", type=decimal.Decimal) # p, t
   edit_parser.add_argument("--from", dest="start", type=parse_date) # b, l
   edit_parser.add_argument("--to", dest="end", type=parse_date) # b, l
   edit_parser.add_argument("--date", type=parse_date) # t
   edit_parser.add_argument("--group") # t
   edit_parser.add_argument("--link") # b, l
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

class InvalidSelectorError(Exception):
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

BUDGET, LEDGER, PLANNED, TRANSACTION = 0, 1, 2, 3

def selector(args):
   """
   returns an integer indicating which selector the given args object designates.
   0: budget
   1: ledger
   2: planned_entry
   3: transaction_entry
   """
   if args.transaction and args.ledger:
      return TRANSACTION
   elif args.planned and args.budget:
      return PLANNED
   elif args.ledger:
      return LEDGER
   elif args.budget:
      return BUDGET
   else:
      return None

def target_budget(bud_choice, budgets, use_id, use_regex):
   "return the target budget id"
   if not bud_choice:
      raise InvalidSelectorError("no budget specified")
   if not budgets:
      raise NotInitializedError("no budgets created")
   if use_id:
      return bud_choice
   else:
      return parse_choice(budgets, bud_choice, regex=use_regex)

def target_ledger(led_choice, ledgers, use_id, use_regex):
   """return the target ledger id. if ledger not specified, raises InvalidSelectorError.
   if the passed ledgers parameter is not defined, then raises NotInitializedError"""
   if not led_choice:
      raise InvalidSelectorError("no ledger specified")
   if not ledgers:
      raise NotInitializedError("no ledgers created")
   if use_id:
      return led_choice
   else:
      return parse_choice(ledgers, led_choice, regex=use_regex)

def target_planned(planned_choice, bud_choice, budgets, use_id, use_regex):
   "return the target budget id, and the target planned entry id"
   if not planned_choice or not bud_choice:
      raise InvalidSelectorError("no budget or planned entry specified")
   if not budgets:
      raise NotInitializedError("no budgets created")
   if use_id:
      if bud_choice not in budgets:
         raise DataNotFoundError(f"budget {bud_choice} not found")
      elif planned_choice not in budgets[bud_choice]:
         raise DataNotFoundError(f"{planned_choice} not a planned entry in budget {bud_choice}")
      return bud_choice, planned_choice
   else:
      budget_id = parse_choice(budgets, bud_choice, regex=use_regex)
      if not budget_id:
         raise DataNotFoundError(f"budget {bud_choice} not found")
      planned_id = parse_choice(budgets[budget_id], planned_choice, 
                                regex=use_regex, key=lambda entry: entry[1].name,
                                print_out=lambda entry: f"{entry[1].name} <{entry[0]}>")
      if not planned_id:
         raise DataNotFoundError(f"{planned_choice} not a planned entry in {bud_choice}")
      return budget_id, planned_id

def target_transaction(tran_choice, led_choice, ledgers, use_id, use_regex):
   "return the target ledger id, and the target transaction id"
   if not tran_choice or not led_choice:
      raise InvalidSelectorError("no ledger or transaction specified")
   if not ledgers:
      raise NotInitializedError("no ledgers created")
   if use_id:
      if led_choice not in ledgers:
         raise DataNotFoundError(f"ledger {led_choice} not found")
      elif tran_choice not in ledgers[led_choice]:
         raise DataNotFoundError(f"{tran_choice} not a transaction in ledger {led_choice}")
      return led_choice, tran_choice
   else:
      ledger_id = parse_choice(ledgers, led_choice, regex=use_regex)
      if not ledger_id:
         raise DataNotFoundError(f"ledger {led_choice} not found")
      transaction_id = parse_choice(ledgers[ledger_id], tran_choice,
                                    regex=use_regex, key=lambda tran: tran.name,
                                    print_out=lambda tran: tran.name)
      return ledger_id, transaction_id

OBJ_SELECT = dict(zip(range(4), (target_budget, target_ledger, target_planned, target_transaction)))

# create --------------

def create_and_write_budget(args, new_budget_id, budgets, end):
   name = args.name or f"Budget {new_budget_id}"
   budgets[new_budget_id] = budget.Budget(name, args.start, end)
   write_data(budgets, budget_path, hook=obj_to_json_budgets)

def create_and_write_ledger(args, new_ledger_id, ledgers, end):
   name = args.name or f"Ledger {new_ledger_id}"
   ledgers[new_ledger_id] = ledger.Ledger(name, args.start, end)
   write_data(ledgers, ledger_path, hook=obj_to_json_ledgers)

def create_handle(args, save_data):
   links = retrieve_data(linker_path, hook=linker.Linker.from_json)
   budgets = retrieve_data(budget_path, hook=json_to_obj_budgets) or dict()
   ledgers = retrieve_data(ledger_path, hook=json_to_obj_ledgers) or dict()
   end = args.end or args.start + datetime.timedelta(weeks=4)

   if args.only == "budget":
      save_data["last_budget"] += 1
      new_budget_id = save_data["last_budget"]
      create_and_write_budget(args, new_budget_id, budgets, end)
      if args.link:
         ledger_link = (args.link if args.use_id 
            else parse_choice(ledgers, args.link, regex=args.use_regex))
         if not ledger_link or ledger_link not in ledgers:
            raise DataNotFoundError(f"ledger with id {ledger_link} not found")
         links.create_link(new_budget_id, ledger_link)

   elif args.only == "ledger":
      save_data["last_ledger"] += 1
      new_ledger_id = save_data["last_ledger"]
      create_and_write_ledger(args, new_ledger_id, ledgers, end)
      if args.link:
         budget_link = (args.link if args.use_id 
            else parse_choice(budgets, args.link, regex=args.use_regex))
         if not budget_link or budget_link not in budgets:
            raise DataNotFoundError(f"budget with id {budget_link} not found")
         links.create_link(budget_link, new_ledger_id)

   else:
      save_data["last_budget"] += 1
      new_budget_id = save_data["last_budget"]
      create_and_write_budget(args, new_budget_id, budgets, end)

      save_data["last_ledger"] += 1
      new_ledger_id = save_data["last_ledger"]
      create_and_write_ledger(args, new_ledger_id, ledgers, end)

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
   links = retrieve_data(linker_path, hook=linker.Linker.from_json)

   select = selector(args)
   if not select:
      raise InvalidSelectorError(f"not a valid selector")
   target = OBJ_SELECT[select]
   if select == BUDGET:
      del budgets[target(args.budget, budgets, args.use_id, args.use_regex)]
   elif select == LEDGER:
      del ledgers[target(args.ledger, ledgers, args.use_id, args.use_regex)]
   elif select == PLANNED:
      budget_id, planned_id = target(args.planned, args.budget, budgets, 
                                     args.use_id, args.use_regex)
      budgets[budget_id].section(planned_id).remove(planned_id)
   else:
      ledger_id, transaction_id = target(args.transaction, args.ledger, ledgers, 
                                         args.use_id, args.use_regex)
      ledgers[ledger_id].remove(transaction_id)

   write_data(budgets, budget_path, hook=obj_to_json_budgets)
   write_data(ledgers, ledger_path, hook=obj_to_json_ledgers)
   write_data(links, linker_path, hook=linker.Linker.to_json)
      
def edit_handle(args, save_data): # edit links
   budgets = retrieve_data(budget_path, hook=json_to_obj_budgets)
   ledgers = retrieve_data(ledger_path, hook=json_to_obj_ledgers)
   links = retrieve_data(linker_path, hook=linker.Linker.from_json)
   select = selector(args)
   if not select:
      raise InvalidSelectorError(f"not a valid selector")
   target = OBJ_SELECT[select]
   if select == BUDGET:
      target_budget = budgets[target(args.budget, budgets, args.use_id, args.use_regex)]
      target_budget.name = args.name or target_budget.name
      target_budget.start = args.start or target_budget.start
      target_budget.end = args.end or target_budget.end
      if args.link:
         pass
   elif select == LEDGER:
      target_ledger = ledgers[target(args.ledger, ledgers, args.use_id, args.use_regex)]
      target_ledger.name = args.name or target_ledger.name
      target_ledger.start = args.start or target_ledger.start
      target_ledger.end = args.end or target_ledger.end
      if args.link:
         pass
   elif select == PLANNED:
      planned, bud = target(args.planned, args.budget, budgets, args.use_id, args.use_regex)
      _, target_planned = budgets[bud][planned]
      target_planned.name = args.name or target_planned.name
      target_planned.expected = args.amount or target_planned.amount
   else:
      trans, led = target(args.transaction, args.ledger, ledgers, args.use_id, args.use_regex)
      target_trans = ledgers[led][trans]
      target_trans.name = args.name or target_trans.name
      target_trans.amount = args.amount or target_trans.amount
      target_trans.date = args.date or target_trans.date
      if args.group:
         pass

   # ("--name") # all
   # ("--amount", type=decimal.Decimal) # p, t
   # ("--from", dest="start", type=parse_date) # b, l
   # ("--to", dest="end", type=parse_date) # b, l
   # ("--date", type=parse_date) # t
   # ("--group") # t
   # ("--link") # b, l

def transaction_handle(args, save_data):
   pass
   
# endregion

# ---------------------
# END
# ---------------------

if __name__ == "__main__":
   main()
