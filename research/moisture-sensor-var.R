library(dplyr)

MOISTURE <- read.csv("./moisture-shortcircuit.csv", head = TRUE, sep=",");
#str(MOISTURE)
setups <- group_by(MOISTURE, SLEEP_TIME_MOISTURE, MOISTURE_NSAMPLE, MOISTURE_NSAMPLE_TIME)
summarise(setups, stddev = sd(VALUE))
