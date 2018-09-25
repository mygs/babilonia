library(dplyr)
setwd("/data/github/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

analyze <- function(filename){
  print('===========================================================================')
  print(toupper(filename))
  moisture_data <- read.csv(filename, head = TRUE, sep=",");
  moisture_data <- group_by(moisture_data, SLEEP_TIME_MOISTURE, MOISTURE_NSAMPLE, MOISTURE_NSAMPLE_TIME)
  summarise(moisture_data, count = n(), mean = mean(VALUE), stddev = sd(VALUE))
}

analyze("./moisture-nickelchromeplate-soildry.csv")
analyze("./moisture-nickelchromeplate-soilwet.csv")
analyze("./moisture-nickelchromeplate-supersoilwet.csv")
analyze("./moisture-nickelchromeplate-supersoilwet2.csv")
analyze("./moisture-nickelchromeplate-water.csv")
analyze("./moisture-nickelchromeplate-water2.csv")
analyze("./moisture-shortcircuit.csv")
analyze("./moisture-soilwet.csv")
analyze("./moisture-supersoilwet.csv")
analyze("./moisture-water.csv")
