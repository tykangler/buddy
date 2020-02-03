"""
Monthly BalanceTracker Tracker
Income -> Curr Balance
Debt -> True Balance
Fixed Expenses -> Dollar Amount
Variable Expenses -> Percentage or Dollar Amount
Discretionary Expenses
---------
Debt will be used to report true balance, but non-debt balance
will be reported as well
"""

from pathlib import Path
import os
import sys
import budget
import interface
import command
import json

def retrieve_budget(file_path, prompt):
   """
   searches file_path for budget data. if file is not found, then prompts
   user to add planned amounts.
   returns a dictionary of categories to category data
   """
   if os.path.isfile(file_path):
      with open(file_path) as data:
         budget_data = json.load(data, object_hook=budget.Balance.from_json)
   else:
      if input(prompt) == 'y':
         budget_data = {name: budget.Category(exp) 
                        for name, exp in interface.collect_input(arrow=interface.INPUT_ARRROW)}
      else:
         budget_data = None
   return budget.Balance(budget_data)

def main():
   income_file = os.path.join(Path.home(), r"buddy\income.json")
   expense_file = os.path.join(Path.home(), r"buddy\expense.json")
   prompt = "No {0} found, add planned {0} (y/n)? " 

   income_balance = retrieve_budget(income_file, prompt.format("income"))
   expense_balance = retrieve_budget(expense_file, prompt.format("expenses"))

   full_budget = budget.Budget(income_balance, expense_balance)

   registry = {"view": ("view budget plan with options",
                        command.Command([], full_budget.view)),
               "status": ("view current income and spending",
                          command.Command([], full_budget.status)),
               "add": ("add cashflow categories to the budget plan",
                       command.Command([], full_budget.add)), 
               "remove": ("remove cashflow categories from the budget plan",
                          command.Command([], full_budget.remove)),
               "spend": ("spend some money",
                         command.Command([], full_budget.spend)),
               "earn": ("add income",
                        command.Command([], full_budget.earn))}

   interface.print_dashboard({name: registry[name][0] for name in registry})
   for request in interface.collect_input(arrow=interface.COMMAND_ARROW):
      print(request)
      pass

if __name__ == "__main__":
   main()