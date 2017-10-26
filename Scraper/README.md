# DataCollectorBBall

## Requirements

Run the following commands before executing `beautifulSoupSelenium.py`

1. `pip install -r requirements.txt`

Now create create a config.json file in the nbaStats director with the following format:

```
{
    host: "<host_ip>",
    user: "<username>",
    pwd: "<super_secret_password>",
    db: "<database_name>"
}
```

## Running `beautifulSoupSelenium.py`:

Desc: Get all pids and names of specified date
Modifiers(Required):
`-db`: push to remote sql db
`-print`: print to terminal

`python beautifulSoupSelenium.py pids <date> <modifier>`

Desc: Get all pids and names
Modifiers(Required):
`-db`: push to remote sql db
`-print`: print to terminal

`python beautifulSoupSelenium.py all_pids <modifier>`

Desc: Get all player matches
UNDER CONSTRUCTION

`python beautifulSoupSelenium.py pmatches`