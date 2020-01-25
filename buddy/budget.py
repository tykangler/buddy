from decimal import Decimal, getcontext, Context
import datetime

"""
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
   
   def actual_amount(self):
      return sum([t.amount for t in self.transactions])

   def expected_amount(self):
      return self.expected

   def all_transactions(self):
      return self.transactions

class Budget:
   """
   tracks expected and actual planned dollar amounts 
   """

   EXP = 0
   ACT = 1
   VAR = 2

   def __init__(self, categories: dict=None):
      self.categories = categories if categories else {} # types already instantiated

   def __iter__(self):
      """
      returns an iterator through Budget categories.
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
      expected_total = sum([self[entry][Budget.EXP] for entry in self])
      actual_total = sum([self[entry][Budget.ACT] for entry in self])
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
