class Assigner:
   """
      Use to assign id values to different objects. A new set of id values are 
   created for each newly created object. Under each id value, a new set of 
   id values can be created. id's are created with a starting value of 0.
   args:
      id_spaces (list): a list of names for id spaces
   """

   class Count:
      "modified version of itertools.count which allows peeking into the current state"
      def __init__(self, start=0, step=1):
         self._step = step
         self._current = start
         self._started = False

      @property
      def current(self):
         return self._current

      @property
      def step(self):
         return self._step

      def __iter__(self):
         return self
         
      def __next__(self):
         ret_val = self._current
         self._current += self._step
         return ret_val

      def __repr__(self):
         return f"Assigner.Count({self.current})"

      def __str__(self):
         return repr(self)

   def __init__(self, id_spaces=None):
      id_spaces = id_spaces if id_spaces else []
      self._id_spaces = {name: list() for name in id_spaces}

   @classmethod
   def from_json(cls, obj):
      new_assigner = cls()
      list_count_obj = lambda id_list: [Assigner.Count(next_id) for next_id in id_list]
      new_assigner._id_spaces = {name: list_count_obj(obj[name]) for name in obj}

   def to_json(self):
      list_next_ids = lambda id_list: [counter.current for counter in id_list]
      return dict(id_spaces={name: list_next_ids(self._id_spaces[name]) 
                             for name in self._id_spaces})

   def next_id(self, name, id_val=None): # next("budget", 2), next("ledger", 3)
      if name not in self._id_spaces:
         raise ValueError(f"name is not a valid id space")
      if id_val:
         if id_val >= len(self._id_spaces[name]) or id_val < 0:
            raise ValueError(f"{id_val} not yet assigned")
         return next(self._id_spaces[name][id_val])
      else:
         self._id_spaces[name].append(self.Count())
         return len(self._id_spaces[name]) - 1
