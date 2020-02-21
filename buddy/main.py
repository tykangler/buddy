from pathlib import Path
import os
import budget
import argparse
import json
import form

INTRO = "Hi {0}! I'm Buddy!"

def main():
   data_dir = os.path.join(Path.home(), "buddy")
   income_path = os.path.join(data_dir, "income.json")
   expense_path = os.path.join(data_dir, "expense.json")
   user_path = os.path.join(data_dir, "user.json")

   user_data = retrieve_user(user_path, 
                             message="No user data found...", 
                             prompts=["Name: "])
   parser = define_parser(user_data)

   args = parser.parse_args()
   income = retrieve_balance(income_path) or budget.Budget()
   expense = retrieve_balance(expense_path) or budget.Budget()

   args.func(args, income, expense)
   user_data["last_id"] = args.last_id

   with open(user_path) as output_user:
      json.dump(user_data, output_user)
   with open(income_path) as output_income:
      json.dump(income, output_income, default=income.to_json)
   with open(expense_path) as output_expense:
      json.dump(expense, output_expense, default=expense.to_json)

def define_parser(user_data):
   parser = argparse.ArgumentParser(description=INTRO.format(user_data["name"]))
   parser.set_defaults(last_id=user_data["last_id"])
   subparsers = parser.add_subparsers(dest="command")
   id_parser = argparse.ArgumentParser(add_help=False)
   id_parser.add_argument("id", type=int)

   date_group_parser = argparse.ArgumentParser(add_help=False)
   date_group_parser.add_argument("--date", "-d", type=form.parse_date)
   date_group_parser.add_argument("--group", "-g", type=int)

   view_parser = subparsers.add_parser("view", help="view budget plan")
   view_parser.add_argument("what", choices={"planned", "actual", "all"}, nargs="?", default="all")
   # view_parser.set_defaults(func=view_handle)

   add_parser = subparsers.add_parser("add", help="add cashflow categories to the budget plan")
   add_parser.add_argument("budget", choices={"income", "i", "expense", "e"})
   add_parser.add_argument("entries", nargs="*", action=SeqToDict)
   add_parser.set_defaults(func=add_handle)

   remove_parser = subparsers.add_parser("remove", help="remove cashflow categories from the budget plan",
                                         parents=[id_parser])
   remove_parser.set_defaults(func=remove_handle)

   edit_parser = subparsers.add_parser("edit", help="edit groups or transactions", 
                                       parents=[id_parser, date_group_parser])
   edit_parser.add_argument("--name", "-n")
   edit_parser.add_argument("--amount", "-a", type=budget.Money)
   edit_parser.set_defaults(func=edit_handle)

   transaction_parser = argparse.ArgumentParser(add_help=False, parents=[date_group_parser])
   transaction_parser.add_argument("name")
   transaction_parser.add_argument("amount", type=budget.Money)
   transaction_parser.set_defaults(func=transaction_handle)

   subparsers.add_parser("spend", help="spend some money", parents=[transaction_parser])
   subparsers.add_parser("earn", help="add income", parents=[transaction_parser])
   return parser

class SeqToDict(argparse.Action):
   def __call__(self, parser, namespace, values, option_string=None):
      d = dict(zip(*[iter(values)] * 2))
      setattr(namespace, self.dest, {key: budget.Money(d[key]) for key in d})

def retrieve_user(path, *, message="", prompts=None):
   """searches file path for user data. if file not found then prompts user to
   enter data. returns a dict with keys corresponding to user data"""
   if os.path.isfile(path):
      with open(path, "r") as file_data:
         return json.load(file_data)
   else:
      print(message)
      return {prompt: input(prompt) for prompt in prompts}

def retrieve_balance(path, *, object_hook=budget.Budget.from_json):
   if os.path.isfile(path):
      with open(path, "r") as file_data:
         return json.load(file_data, object_hook=object_hook)
   return None

def add_handle(args, income_budget, expense_budget):
   def add_groups(bud):
      group_id = args.last_id
      for group_name in args.entries:
         group_id += 1
         bud.add_group(group_id, group_name, args.entries[group_name])
      return group_id
   if args.budget == "income" or args.budget == "i":
      last_id = add_groups(income_budget)
   else:
      last_id = add_groups(expense_budget)
   args.last_id = last_id

def remove_handle(args, income_budget, expense_budget):
   if args.id in income_budget:
      income_budget.remove_entry(args.id)
   elif args.id in expense_budget:
      expense_budget.remove_entry(args.id)
   else:
      print("No entry found")

def edit_handle(args, income_budget, expense_budget):
   def edit_entry(bud):
      if bud.is_group(args.id):
         group = bud.group(args.id)
         group.name = args.name if args.name else group.name
         group.expected = args.amount if args.amount else group.expected
      else:
         tran = bud.transaction(args.id)
         tran.name = args.name if args.name else tran.name
         tran.amount = args.amount if args.amount else tran.amount
         tran.date = args.date if args.date else tran.date
         if args.group:
            bud.remove_transaction(args.id)
            trans_args = dict(name=tran.name, amount=tran.amount, date=tran.date)
            bud.add_transaction(args.group, args.id, **trans_args)
   if args.id in income_budget:
      edit_entry(income_budget)
   elif args.id in expense_budget:
      edit_entry(expense_budget)
   else:
      print("No entry found")

def transaction_handle(args, income_budget, expense_budget):
   args.last_id += 1
   trans_args = dict(name=args.name, date=args.date, amount=args.amount)
   if args.command == "earn":
      income_budget.add_transaction(args.group, args.last_id, **trans_args)
   else:
      expense_budget.add_transaction(args.group, args.last_id, **trans_args)

if __name__ == "__main__":
   main()