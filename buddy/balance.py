from decimal import Decimal, getcontext, Context
import json
import itertools

"""
income budget json file --
{
   0: {
      'name': 'work' 
      'expected': 1500, 
      'transactions': { 
         0: {
            'name': 'sbux', 
            'amount': 400, 
            'date': 01/15/2020
         },
         1: {
            'name': 'sbux', 
            'amount': 500, 
            'date': 01/01/2020
         }
      }
   },
}

budget python obj input --
{
   0: <type 'Group', 
       name='work',
       expected=1500, 
       transactions={
          0: <type 'Transaction'
              name='sbux'
              amount=400,
              date='01/15/2020' # consider datetime object
          >,
          1: <type 'Transaction'
              name='sbux',
              amount=500,
              date='01/01/2020'
       }
}
"""
def create_assigner(next_id=0):
   return itertools.count(next_id)

class CorruptedInputError(KeyError):
   """
   budget input file has missing or incorrect keys, or an excess of keys
   """
   def __init__(self, inp, msg=None):
      self.corrupted = inp
      self.msg = msg if msg else ""

class Money(Decimal):
   """
   class representing dollar amounts. subclasses Decimal and overrides
   string and repr functionality
   """
   PRECISION = 2

   def __str__(self):
      return str(self.quantize(Decimal(10) ** -Money.PRECISION))

   def __repr__(self):
      return f"Money({self})"
   
class Transaction:
   """
   a single line item in a financial statement. Contains fields for name, date, and 
   amount earned in transaction
   """
   def __init__(self, name, amount, date):
      self.name = name
      self.amount = Money(amount)
      self.date = date

   @classmethod
   def from_json(cls, obj):
      return cls(**obj)

   def __repr__(self):
      return f"Transaction({self.name}, {self.date}, {self.amount})"

class Group:
   """
   A cash flow category. Contains an additional field, expected, over Transaction
   representing the planned amount, as well as all transactions within the category
   """
   def __init__(self, name, expected=0.00):
      self.name = name
      self.expected = Money(expected)
      self.transactions = {}
      self.actual = Money(0)

   @classmethod
   def from_json(cls, obj):
      transactions = obj["transactions"]
      transactions = {id_num: Transaction.from_json(transactions[id_num])
                      for id_num in transactions}
      new_group = cls(obj["name"], obj["expected"])
      new_group.transactions = transactions
      return new_group

   def __getitem__(self, id_num):
      return self.transactions[id_num]

   def __contains__(self, id_num):
      return id_num in self.transactions
   
class Budget:
   """
   tracks expected and actual planned dollar amounts
   """

   def __init__(self, assigner):
      self.assigner = assigner
      self.groups = {}
      self.trans_to_group = {}
      self.planned = Money(0)
      self.actual = Money(0)

   @classmethod
   def from_json(cls, obj):
      return cls({id_num: Group.from_json(obj[id_num]) for id_num in obj})

   def __iter__(self):
      return iter(self.groups)

   def __getitem__(self, id_num):
      if id_num in self.groups:
         return self.groups[id_num]
      elif id_num in self.trans_to_group:
         group_id = self.trans_to_group[id_num]
         return self.groups[group_id][id_num]
      else:
         raise ValueError("entry not found with id number")

   def __contains__(self, id_num):
      return id_num in self.groups or id_num in self.trans_to_group

   def total_planned(self):
      return self.planned

   def total_actual(self):
      return self.actual

   def num_groups(self):
      return len(self.groups)

   def num_transactions(self):
      return len(self.trans_to_group)

   def is_group(self, id_num):
      return id_num in self.groups

   def is_transaction(self, id_num):
      return id_num in self.trans_to_group

   def add_group(self, **group_args): 
      group_id = next(self.assigner)
      self.planned += Money(group_args["expected"])
      self.groups[group_id] = Group(**group_args)
      return group_id

   def remove_group(self, group_id):
      if group_id not in self.groups:
         raise ValueError("group not found")
      amt_to_remove_planned = self.groups[group_id].expected
      amt_to_remove_actual = self.groups[group_id].actual
      for transaction_id in self.groups[group_id].transactions:
         del self.trans_to_group[transaction_id]
      del self.groups[group_id]
      self.planned -= amt_to_remove_planned
      self.actual -= amt_to_remove_actual

   def remove_transaction(self, transaction_id):
      if transaction_id not in self.trans_to_group:
         raise ValueError("transaction not found")
      amt_to_remove = self.groups[transaction_id].amount
      del self.groups[transaction_id]
      del self.trans_to_group[transaction_id]
      self.actual -= amt_to_remove

   def remove(self, id_num):
      if id_num in self:
         if self.is_group(id_num):
            self.remove_group(id_num)
         else:
            self.remove_transaction(id_num)

   def add_transaction(self, group_id, **trans_args):
      transaction_id = next(self.assigner)
      amt_to_add = Money(trans_args["amount"])
      group = self.groups[group_id]

      self.trans_to_group[transaction_id] = group_id
      group[transaction_id] = Transaction(**trans_args)
      self.actual += amt_to_add
      group.actual += amt_to_add

      return transaction_id