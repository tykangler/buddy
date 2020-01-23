"""
Monthly Budget Tracker
Income -> Curr Balance
Debt -> True Balance
Fixed Expenses -> Dollar Amount
Variable Expenses -> Percentage or Dollar Amount
Discretionary Expenses
---------
Debt will be used to report true balance, but non-debt balance
will be reported as well
"""
"""
income budget json file --
{ // category -> category data, remains dict
   'work': { // category data, convert to object
      'expected': 1500, 
      'transactions': [ // an array of transactions, remains list
         { // transaction data, convert to object
            'name': 'sbux', 
            'amount': 400, 
            'date': 01/15/2020
         },
         {
            'name': 'sbux', 
            'amount': 500, 
            'date': 01/01/2020
         }
      ]
   },
}
"""

import os
from pathlib import Path
import sys
import json
import budget
import interface
import commands

class CorruptedInputError(KeyError):
   """
   Budget input file has missing or incorrect keys, or an excess of keys
   """
   def __init__(self, inp, msg=None):
      self.corrupted = inp
      self.msg = msg if msg else ""

def verify_keys(func):
   "raises CorruptedInputError if a key is not found within the passed object"
   def func_with_exception(obj):
      try:
         func(obj)
      except (KeyError, TypeError):
         raise CorruptedInputError(obj)
   return func_with_exception

@verify_keys
def convert_transaction(obj: dict):
   return budget.Transaction(**obj)

@verify_keys
def convert_category(obj: dict):
   transactions = [convert_transaction(trans_data) for trans_data in obj["transactions"]]
   return budget.Category(obj["expected"], transactions)

def decode_budget_json(obj):
   """
   top level dictionary remains. category data is converted to Category, and transaction
   data is converted to Transaction
   """
   return {cat: convert_category(obj[cat]) for cat in obj}

def construct_budget(file_path, prompt):
   """
   searches file_path for budget data. if file is not found, then prompts
   user to add planned amounts.
   returns a dictionary of categories to category data
   """
   if os.path.isfile(file_path):
      with open(file_path) as json_data:
         budget_data = json.load(json_data, object_hook=decode_budget_json)
   else:
      budget_data = {name: budget.Category(exp) 
                     for name, exp in interface.collect_input(arrow=interface.INPUT_ARRROW)}
   return budget.Budget(budget_data)

if __name__ == "__main__":
   income_file = os.path.join(Path.home(), r"buddy\income.json")
   expense_file = os.path.join(Path.home(), r"buddy\expense.json")
   prompt_fstring = "No {0} found, add planned {0} (y/n)? " 

   income_budget = construct_budget(income_file, prompt_fstring.format("income"))
   expense_budget = construct_budget(expense_file, prompt_fstring.format("expenses"))

   interface.print_dashboard()
   dispatch = commands.Dispatch({})
   for command in interface.collect_input(arrow=interface.COMMAND_ARROW):
      dispatch.execute(command.Request)