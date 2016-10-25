# Transfer Target Generator: Database generator.
Database generator for the [Transfer Target Generator](https://github.com/craciunBogdan/transfer-generator) app.

3 Python scripts that build a database that is used by the Transfer Target Generator app. These scripts take all of the information from [transfermarkt](http://www.transfermarkt.co.uk).

Run the 3 scripts in the following order:
  1. ```league_generator.py``` (will take around 5 seconds)
      This generates the Leagues table which contains every league.
  2. ```team_generator.py``` (will take around 4 minutes)
      This generates the Teams table which contains every team from the leagues generated previously.
  3. ```player_generator.py``` (will taker around 40 minutes)
      This generates the Players table which contains every player from the teams generated previously.
      
This will create a database called ```main.db``` which can then be used for the Transfer Target Generator app.
