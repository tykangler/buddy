from decimal import Decimal, getcontext, Context
import datetime

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

budget python obj input --
{
   'income': <type 'Category', 
              expected=1500, 
              actual=[
                 <type 'Transaction'
                  name='sbux'
                  amount=400,
                  date='01/15/2020' # consider datetime object
                 >,
                 <type 'Transaction'
                  name='sbux',
                  amount=500,
                  date='01/01/2020'
              ]
}
"""
         
class CorruptedInputError(KeyError):
   """
   BalanceTracker input file has missing or incorrect keys, or an excess of keys
   """
   def __init__(self, inp, msg=None):
      self.corrupted = inp
      self.msg = msg if msg else ""

class Money(Decimal):
   """
   class representing dollar amounts. subclasses Decimal and overrides
   string and repr functionality
   """
   PREC = 2

   def __str__(self):
      return self.quantize(Decimal(10) ** -Money.PRECISION)

   def __repr__(self):
      return f"Money({self})"
   
class Transaction:
   """
   a single line item in a financial statement. Contains fields for name, date, and 
   amount earned in transaction
   """
   def __init__(self, name, date, amount=0.00):
      self.name = name
      self.date = datetime.date(date)
      self.amount = Money(amount)

   @classmethod
   def from_json(cls, obj):
      return cls(**obj)

   def __repr__(self):
      return f"Transaction({self.name}, {self.date}, {self.amount})"

class Category:
   """
   A cash flow category. Contains an additional field, expected, over Transaction
   representing the planned amount, as well as all transactions within the category
   """
   def __init__(self, expected=0.00, transactions=None):
      self.expected = Money(expected)
      # stack of Transaction(s)
      self.transactions = transactions if transactions else []

   @classmethod
   def from_json(cls, obj):
      transactions = [Transaction.from_json(trans_data) for trans_data in obj["transactions"]]
      return cls(obj["expected"], transactions)
   
   def actual_amount(self):
      return sum([t.amount for t in self.transactions])

   def expected_amount(self):
      return self.expected

   def all_transactions(self):
      return self.transactions

class Balance:
   """
   tracks expected and actual planned dollar amounts 
   """

   EXP = 0
   ACT = 1
   VAR = 2

   def __init__(self, categories: dict=None):
      self.categories = categories if categories else {} # types already instantiated

   @classmethod
   def from_json(cls, obj):
      return cls({Category.from_json(obj[cat]) for cat in obj})

   def __iter__(self):
      """
      returns an iterator through Balance categories.
      """
      return iter(self.categories)

   def __getitem__(self, category):
      """
      returns a tuple (expected, actual) associated with category
      """
      assoc_data = self.categories[category]
      expected = assoc_data.expected_amount() 
      actual = assoc_data.actual_amount() 
      return expected, actual

   def total(self):
      """
      returns a tuple (expected, actual), each field representing the total
      of that field
      """
      expected_total = sum([self[entry][Balance.EXP] for entry in self])
      actual_total = sum([self[entry][Balance.ACT] for entry in self])
      return expected_total, actual_total

   def transactions(self, category):
      """
      returns a list of transactions under category, sorted by date with most recent first
      """
      return self.categories[category].all_transactions()

   def add(self, category, expected=0.00, transactions=None):
      self.categories[category] = Category(expected, transactions)

   def remove(self, category):
      if category in self.categories:
         del self.categories[category]

class Budget:
   def __init__(self, income_data, expense_data):
      self.income = income_data
      self.expense = expense_data

   def view(self, *args, **kwargs):
      pass

   def status(self, *args, **kwargs):
      pass

   def add(self, *args, **kwargs):
      pass

   def remove(self, *args, **kwargs):
      pass

   def spend(self, *args, **kwargs):
      pass

   def earn(self, *args, **kwargs):
      pass