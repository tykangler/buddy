def view(formatter, *budgets):
   pass

def add(to_add: dict, budget):
   for group_name in to_add:
      budget.add_group(group_name, to_add[group_name])

def remove(id_num, budget):
   budget.remove(id_num)

def spend_earn(group_id, name, amount, date, budget):
   budget.add_transaction(group_id, name=name, amount=amount, date=date)