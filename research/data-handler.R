# Handling data with R: just a reference


# reading csv file ...
# HEADER: NODE,TIMESTAMP,VALUE,SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME
MOISTURE <- read.csv("./moisture-shortcircuit.csv", head = TRUE, sep=",");
head(MOISTURE$SLEEP_TIME_MOISTURE)
