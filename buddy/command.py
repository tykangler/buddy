# Exception Classes

class InvalidRequestError(ValueError):
   def __init__(self, request):
      self.request = request

class CommandError(KeyError):
   def __init__(self, arg):
      self.arg = arg

# Class and Function Definitions

def _index_of_next_opt(word_list, possible_opts, *, start=0):
   """returns the index in word_list where mark is the first letter. 
   returns the length of word_list if not found."""
   for i in range(start, len(word_list)):
      if word_list[i] in possible_opts:
         return i
   return len(word_list)

class Command:

   PARSED_ARGS = 0
   PARSED_OPTS = 1

   def __options_to_dict(self, word_list: list):
      "pre: word_list is a list containing only options and filters"
      opts = {}
      opt_start = 0
      opt_end = _index_of_next_opt(word_list, self.possible_opts, start=opt_start + 1)
      while opt_end < len(word_list):
         opts[word_list[opt_start]] = word_list[opt_start + 1:opt_end]
         opt_start = opt_end
         opt_end = _index_of_next_opt(word_list, self.possible_opts, start=opt_start + 1)
      opts[word_list[opt_start]] = word_list[opt_start + 1:opt_end]
      return opts

   def __init__(self, possible_opts, handler):
      self.possible_opts = set(possible_opts)
      self.handler = handler

   def parse(self, parse_string):
      """Given a string of arguments, filters, and options, return a tuple
      of base arguments, and a dictionary mapping option names to values"""
      word_list = parse_string.split()
      if len(word_list) == 0:
         raise InvalidRequestError(parse_string)
      opt_start = _index_of_next_opt(word_list, self.possible_opts)
      args = word_list[:opt_start]
      options = (self.__options_to_dict(word_list[opt_start:]) 
                 if opt_start < len(word_list) else None)
      return args, options

   def execute(self, parsed):
      """Executes the handler associated with this command with the given arguments"""
      args, opts = parsed
      self.handler(*args, **opts)
