# Main Dash

dash = """
Hi I'm Buddy!

view        view budget plan according to options 
status      view current income and spending
add         add a cashflow category to the budget plan
remove      remove a cashflow category to the budget plan
spend       add an expense
earn        add income
"""[1:]

INPUT_ARRROW = "> "
COMMAND_ARROW = ">>> "

def print_dashboard():
   print(dash)

def eofinput(prompt):
   try:
      return input(prompt)
   except EOFError:
      return ""

def collect_input(*, arrow):
   read = eofinput(arrow)
   while read != "":
      yield read.split()
      read = eofinput(arrow)