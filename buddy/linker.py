def find_in_set(iterable, obj, test=None):
   for item in iterable:
      if test == None:
         if item == obj:
            return item
      else:
         if test(item, obj):
            return item
   return None

class Linker:

   class Relationship:
      def __init__(self, budget_id, ledger_id):
         self.budget_id = budget_id
         self.ledger_id = ledger_id
         self.ledger_to_budget_links = dict() # int -> int
         self.budget_to_ledger_links = dict() # int -> set

      def __eq__(self, other):
         return self.budget_id == other.budget_id and self.ledger_id == other.ledger_id

      def budget_entry_exists(self, budget_entry_id):
         return budget_entry_id in self.budget_to_ledger_links

      def ledger_entry_exists(self, ledger_entry_id):
         return ledger_entry_id in self.ledger_to_budget_links

      def budget_link(self, ledger_entry_id):
         return self.ledger_to_budget_links[ledger_entry_id]
      
      def ledger_links(self, budget_entry_id):
         return self.budget_to_ledger_links[budget_entry_id]

      def is_linked(self, budget_entry_id, ledger_entry_id):
         links_exist = (self.ledger_entry_exists(ledger_entry_id) 
                        and self.budget_entry_exists(budget_entry_id))
         return (links_exist and 
                 self.ledger_to_budget_links[ledger_entry_id] == budget_entry_id and
                 ledger_entry_id in self.budget_to_ledger_links[budget_entry_id])

      def remove_link(self, budget_entry_id, ledger_entry_id):
         if self.is_linked(budget_entry_id, ledger_entry_id):
            ledger_links = self.ledger_links(budget_entry_id)
            matched_ledger_id = find_in_set(ledger_links, ledger_entry_id)
            ledger_links.remove(matched_ledger_id)
            del self.ledger_to_budget_links[ledger_entry_id]

      def create_link(self, budget_entry_id, ledger_entry_id):
         if self.ledger_entry_exists(ledger_entry_id):
            self.remove_link(self.budget_link(ledger_entry_id), ledger_entry_id)
         self.ledger_to_budget_links[ledger_entry_id] = budget_entry_id
         if not self.budget_entry_exists(budget_entry_id):
            self.budget_to_ledger_links[budget_entry_id] = set()
         self.budget_to_ledger_links[budget_entry_id].add(ledger_entry_id)

   def __init__(self):
      self.relationships = dict()

   @classmethod
   def from_json(cls, obj):
      pass

   def to_json(self):
      pass

   def __link_exists(self, budget_id, ledger_id, relationship):
      rel_budget_id, rel_ledger_id = relationship.budget_id, relationship.ledger_id
      return budget_id == rel_budget_id and ledger_id == rel_ledger_id

   def relationship(self, budget_id, ledger_id):
      for relationship in self.relationships[budget_id]:
         if self.__link_exists(budget_id, ledger_id, relationship):
            return relationship
      return None

   def create_link(self, budget_id, ledger_id):
      if not self.relationship(budget_id, ledger_id):
         new_relationship = self.Relationship(budget_id, ledger_id)
         self.relationships[budget_id] = set(new_relationship)
         self.relationships[ledger_id] = set(new_relationship)