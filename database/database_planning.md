# Database Architecture

In terms of marginal net. Monthly based Budgeting System.

## Requirements

Store recurring expenses and their frequency.
Store wages to earn and their frequency.
Store planned expenses for a given period.
Store days for wages earned and expenses paid.

## Tables

### Recurring

| id | name        | type | frequency | unit  | amount | begin   | end     |
|----|-------------|------|-----------|-------|--------|---------|---------|
| 0  | rent        | e    | 1         | month | 875    | 09/2020 | 09/2021 |
| 1  | electricity | e    | 2         | month | 35     | 09/2020 | 09/2021 |
| 2  | wifi        | e    | 1         | month | 12.5   | 09/2020 | 09/2021 |
| 3  | utilities   | e    | 1         | month | 65     | 09/2020 | 09/2021 |
| 4  | Laundry     | e    | 1         | month | 25     | 09/2020 | 09/2021 |
| 5  | esd         | i    | 2         | week  | 1489   | 09/2020 | 10/2020 |

### Planned

#### Expenses

| id | name  | type | amount |
|----|-------|------|--------|
| 0  | couch | e    | 60     |

### Days of Transactions

| id | day | flow_id |
|----|-----|---------|
| 0  | 1   | 0       |
| 1  | 1   | 1       |
| 2  | 26  | 2       |
| 3  | 10  | 5       |
| 4  | 26  | 5       |
