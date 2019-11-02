
setwd("~/Development/babilonia/research/moisture-capacitive")


moisture_data <- group_by(read.csv("./water001.csv", head = TRUE, sep=","), 
                          TIMESTAMP,MOISTURE)


COUNT <- length(moisture_data$MOISTURE)
MEDIAN <- median(moisture_data$MOISTURE)
MEAN <- mean(moisture_data$MOISTURE)
SD <- sd(moisture_data$MOISTURE)
MIN <- min(moisture_data$MOISTURE)
MAX <- max(moisture_data$MOISTURE)


