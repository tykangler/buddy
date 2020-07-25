import argparse
import datetime as dt
import json
import math
from decimal import Decimal

import accounts
import dateparse
import journal
import schedule
import user

MAX_BUDGET_ROLL = 50

def main():
   parser = define_arguments()
   args = parser.parse_args()
   try:
      args.func(args)
   except Exception as e:
      print(e)

def define_arguments():
   parser = argparse.ArgumentParser(description="Hello!")
   subparsers = parser.add_subparsers(dest="command")
   define_plan_args(subparsers.add_parser("plan", description="begin a budget plan"))
   define_schedule_args(subparsers.add_parser("schedule", 
      description="schedule changes in accounts"))
   define_remove_args(subparsers.add_parser("remove", description="remove a budget/snapshot"))
   define_view_args(subparsers.add_parser("view", 
      description="view reports of current/planned financial"))
   define_enter_args(subparsers.add_parser("enter", description="enter a transaction"))
   define_config_args(subparsers.add_parser("config", description="settings"))
   define_edit_args(subparsers.add_parser("edit", 
      description="edit transactions/budget entries/schedule entries"))
   return parser
                                              
def define_plan_args(plan_parser: argparse.ArgumentParser):
   plan_parser.add_argument("name")
   plan_parser.add_argument("--from", "-f", type=dateparse.parse_date, 
                            default=dt.date.today(), dest="start")
   plan_parser.add_argument("--to", "-t", type=dateparse.parse_date,
                            default=dt.date.today() + dt.timedelta(weeks=4), dest="end")
   plan_parser.add_argument("--roll", "-r", nargs="?", const=MAX_BUDGET_ROLL, default=0, type=int)
   plan_parser.add_argument("--clone", "-c", nargs="?") # in handler, handle no arg case
   plan_parser.add_argument("--prompt", "-p", action="store_true")

def define_schedule_args(schedule_parser: argparse.ArgumentParser):
   schedule_parser.add_argument("account-name")
   schedule_parser.add_argument("--alias")
   schedule_parser.add_argument("--snap")
   schedule_parser.add_argument("--from", "-f", type=dateparse.parse_date, dest="start")
   schedule_parser.add_argument("--to", "-t", type=dateparse.parse_date, dest="start")
   schedule_parser.add_argument("--length", "-l", type=dateparse.parse_dist)
   schedule_parser.add_argument("--periods", "-p", type=int)
   schedule_parser.add_argument("--prompt", action="store_true")
   schedule_parser.add_argument("--manual", "-m")
   schedule_parser.add_argument("--straight", "-s")
   schedule_parser.add_argument("--recur", "-r")

def define_remove_args(remove_parser: argparse.ArgumentParser):
   remove_parser.add_argument("type", choices={"budget", "planned", "transaction", "schedule"})
   remove_parser.add_argument("name")

def define_view_args(view_parser: argparse.ArgumentParser):
   pass

class ListToDict(argparse.Action):
   def __call__(self, parser, namespace, values, option_string=None):
      d = dict(zip(*[iter(values)] * 2))
      setattr(namespace, self.dest, d)

def define_edit_args(edit_parser: argparse.ArgumentParser):
   "edit transactions, budget entries, schedule entries"
   pass

def define_enter_args(enter_parser: argparse.ArgumentParser):
   enter_parser.add_argument("transaction")
   enter_parser.add_argument("--debit", "-d", nargs="*", action=ListToDict)
   enter_parser.add_argument("--credit", "-c", nargs="*", action=ListToDict)

def define_config_args(config_parser: argparse.ArgumentParser):
   pass

def plan_handle(args):
   pass

def schedule_handle(args):
   pass

def remove_handle(args):
   pass

def view_handle(args):
   pass

def edit_handle(args):
   pass

def enter_handle(args):
   pass

def config_handle(args):
   pass
