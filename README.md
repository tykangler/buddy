# buddy

My best friend. I am terrible at managing my finances. I did not mean 
for this to be a large project, just something quick and dirty.

## Status

| Module | Finished | Tested | Notes |
|:-------|:--------:|:------:|:------|
| budget |    ❌   |   ❌   |       |
| interface |  ❌  |   ✔️   | Untested for long command strings |
| command |   ✔️   |   ❌   | Tests limited, expect dispatch to be implemented in main |

## Issues

### Uneasy

* Factor out json serialization from main into budget
* command->desc and command->handler have same keys, but different values

### TODOs

* Implement handlers for all commands
* Implement command loop
* Factor out formatting to interface
* Budget class to track both income and expense budgets
