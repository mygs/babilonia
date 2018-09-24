library(dplyr)
#suppressPackageStartupMessages(library(dplyr))
#moisture-nickelchromeplate-soilwet.csv
#moisture-nickelchromeplate-supersoilwet.csv
#moisture-nickelchromeplate-water.csv
#moisture-sensor-var.R
#moisture-shortcircuit.csv
#moisture-soilwet.csv
#moisture-supersoilwet.csv
#moisture-water.csv
moisture_nickelchromeplate_soilwet <- read.csv("./moisture-nickelchromeplate-soilwet.csv", head = TRUE, sep=",");
moisture_nickelchromeplate_soilwet <- group_by(moisture_nickelchromeplate_soilwet, SLEEP_TIME_MOISTURE, MOISTURE_NSAMPLE, MOISTURE_NSAMPLE_TIME)
summarise(moisture_nickelchromeplate_soilwet, count = n(), mean = mean(VALUE), stddev = sd(VALUE))
