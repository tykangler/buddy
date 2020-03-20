# Buddy Specification 

Buddy is a budgeting program that allows you to plan income and expenses,
and later report them when they happen. A budget must first be created
with a name, and a date range. Once a budget is created, you can plan 
cash flows. **Multiple budgets** can be created and added to. Upon budget creation,
a **ledger will automatically be created** where you can add report transactions with
a name, date, and amount. You can specify whether to create just a budget or a ledger with
the `only` flag. By default, the date will be today. The ledger's default date range
will be the same as the budget's. Transactions can be grouped under planned categories in 
the corresponding budget if one exists. Reporting can be done with multiple reporting options. 
The user can set defaults and configure the program with the following settings:

* name
* default budget

## ID Specification

Budgets will be represented with their own id-space, with each entry in the budget sharing the id-space.
Ledgers will also be represented with their own id-space, with each transaction sharing the id-space.
Budget entries and ledger entries can be linked so that ledger entries can be grouped under budget entries.
Because budgets and ledgers live in their own id-space, budgets and ledgers themselves must be linked so that
budget and ledger entries can be linked. For budgets and ledgers to be linked, they must share the same date range.
Budgets and ledgers created without the `only` command are automatically linked.

## Commands

* create
* plan
* remove
* edit 
* spend
* earn

### create

create a budget plan

| Arguments | Description | Default |
|-----------|-------------|---------|
| only | ledger or budget | none |
| name | name of the plan | Budget {id} |
| from_date | beginning of date range | today |
| to_date | end of date range | 4 weeks from today |

If no budget file is found, then one will be created with id equal to the next id.

## Reporting

Reporting is done with the `report` command
```
$ buddy report ...
```

### Reports

#### PL View

```  
From 00/00/00 - 00/00/00
----+-------------------------------------+----------+---------+----------
 id |                                     |  planned |  actual | variance
----+-------------------------------------+----------+---------+----------
    | **income**                          | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 |    00/00/00 trans-foo               |          |  000.00 | 
 00 |    00/00/00 trans-po                |          |  000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
 00 | group                               |   000.00 | 0000.00 | +  00.00
 00 |    00/00/00 trans-bar               |          | 0000.00 |
 00 |    00/00/00 trans-ba                |          | 0000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
----+-------------------------------------+----------+---------+----------
    | **expense**                         | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 |    00/00/00 trans-foo               |          |  000.00 | 
 00 |    00/00/00 trans-po                |          |  000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
 00 | group                               |   000.00 | 0000.00 | +  00.00
 00 |    00/00/00 trans-bar               |          | 0000.00 |
 00 |    00/00/00 trans-ba                |          | 0000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
----+-------------------------------------+----------+---------+----------
    | **debt**                            | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 |    00/00/00 trans-foo               |          |  000.00 | 
 00 |    00/00/00 trans-po                |          |  000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
 00 | group                               |   000.00 | 0000.00 | +  00.00
 00 |    00/00/00 trans-bar               |          | 0000.00 |
 00 |    00/00/00 trans-ba                |          | 0000.00 |
 00 |    00/00/00 trans-                  |          | 0000.00 |
----+-------------------------------------+----------+---------+----------
 cash balance                             |   000.00 |  000.00 | -   0.00
 true balance                             |    00.00 |   00.00 | -   0.00
----+-------------------------------------+----------+---------+----------
```

#### Transaction View

View transactions sorted by date

```
From 00/00/00 - 00/00/00
-----+-------------------------------------+---------
  id | Transaction                         |  Amount
-----+-------------------------------------+---------
 000 | 00/00/00 trans-foo                  |  +00.00
  00 |          trans-bar                  | -000.00
 000 | 00/00/00 trans-baz                  |   -0.00
-----+-------------------------------------+---------
Net Gain/Loss                                  +0.00
```

##### Brainstorm 

* 10^ad_digits + remainder = amount
   * ad_digits increase  with every power of 10
   * remainder is not important since it resets every power of 10
   * 10^ad_digits = amount
   * ad_digits = log_10(amount) // 1
* at least 7 characters needed to represent amount (" [+-] n.nn")
* addition of prior 2 calcs results in number of digits for amount
* 9 characters needed for date representation (8 for date and 1 space)
* 1 empty space at end of line, so true width is 55
* Characters for name and space is (55 - (add_digits + 7) - 9)
* if name is at max length, then characters for name and space is made up of just name
* Spaces to print = (55 - (add_digits + 7) - 9 - len(transaction_name))


#### Group View   

```
From 00/00/00 - 00/00/00
----+-------------------------------------+----------+---------+----------
 id |                                     |  planned |  actual | variance
----+-------------------------------------+----------+---------+----------
    | **income**                          | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 | group                               |   000.00 | 0000.00 | +  00.00
----+-------------------------------------+----------+---------+----------
    | **expense**                         | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 | group                               |   000.00 | 0000.00 | +  00.00
----+-------------------------------------+----------+---------+----------
    | **debt**                            | 00000.00 | 0000.00 | - 000.00
----+-------------------------------------+----------+---------+----------
 00 | group                               | 00000.00 | 0000.00 | - 000.00
 00 | group                               |   000.00 | 0000.00 | +  00.00
----+-------------------------------------+----------+---------+----------
 cash balance                             |   000.00 |  000.00 | -   0.00
 true balance                             |    00.00 |   00.00 | -   0.00
----+-------------------------------------+----------+---------+----------
```

#### Summaries

##### Ratio Summaries

Summarize financials. Not too robust right now.

```
As a percentage of total income ($0000.00):
-----------------------------------------
Expenses                        00.00%
Debt                            00.00%
Cash Balance                    00.00%
True Balance                    00.00%
-----------------------------------------

Number of Transactions             00
Number of Groups                   00

Date of Last Transaction     00-00-00
```

### Filters and Options

| name        | description           | keyword | defaults  |
|-------------|-----------------------|---------|-----------|
| view        | transaction, PL, summ |         | PL + summ |
| time        | filter by time frame  |         | month     |
| section     | inc, exp, debt, etc.  |         | all       |
| amount      | filter by amount      |         | all       |
| name        | find literal or regex |         | all       |


## Internals

### Procedure

1. Budgets and Ledgers will be retrieved from file.
    * If a budget file is not found, 

### Object



### File

Budget data and user data are stored in json format.

#### Budget Data

Budget files are stored with object fields mapping to object values.
One file will be kept for all planned budgets.

##### Sample

```
{
    id: {
        section: {
            name: name
            from_date: from_date
            to_date: to_date
            entries: {
                id: {
                    name: name
                    expected: expected
                }
                id: ...
            }
            total: total
        }
        section: ...
    }
}
```

#### Ledger



#### User Data

User data is stored with the following fields. Some can be changed with the config command

| Field   | Description                                      |
|---------|--------------------------------------------------|
| last_id | last id assigned to a group or transaction       |
| default_budget_id | budget id of default budget            |
| name    | name of user                                     |
