class InvalidRequestError(ValueError):
   def __init__(self, request, msg=""):
      self.request = request
      self.msg = msg

class Handler:
   def __init__(self, func=None):
      self.func = func

   def does(self, func):
      self.func = func

class Command:
   def __init__(self, name, options):
      self.name = name
      if options:
         self.options = {opt: Handler() for opt in options}

   def add_option(self, option):
      self.options[option] = Handler()
      return self.options[option]

class Dispatch:
   def __init__(self):
      self.command_dispatch = {}
   
   def add(self, *, command, options=None):
      self.command_dispatch[command] = Command(command, options)
      return self.command_dispatch[command]

   def execute(self, request):
      try:
         if request.command in self.command_dispatch:
            self.command_dispatch[request.command](request.command_args)
         else:
            raise InvalidRequestError(request, "command not implemented")
      except TypeError:
         raise InvalidRequestError(request, 
                  f"{request.command} present, but arguments are invalid")

   def __getitem__(self, command):
      return self.command_dispatch[command]

class Request:
   "expression tree for queries and actions"
   def __init__(self, expression):
      if len(expression) == 0:
         raise InvalidRequestError(expression)
