# Alaska
This code was used for an analysis of Alaska's pairing of house districts to senate districts.

- 01_scraper.py is used to scrape voting data from the Alaska elections website
- 02_merger.py is used to merge this data with demographic data from the census. The resulting csv is in the dropbox as AK2014byprecinct.csv
- 04_check_matchings.py makes predictions for all matchings from a CSV with vote counts for each district (this is based on the Meyer framework)
- 05_heat_map.Rmd is a piece of visaulization code that makes heat maps of partisanship measures
- 06_evaluate_predictions.py is a helper script that shows which districts the model got right/wrong, and whether they were contested or had incumbents
- 07_simulation.py is an attempt to make the Meyer model probabilistic by running simulations from predicted vote counts
- 08_logistic.py abandons the Meyer model and fits a logistic regression to the data
