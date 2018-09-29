library(dplyr)
setwd("/data/github/babilonia/research")
setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

analyze <- function(filename){
  file=paste(paste("./",filename, sep=""),"csv", sep=".");
  moisture_data <- read.csv(file, head = TRUE, sep=",");
  moisture_data <- group_by(moisture_data, SLEEP_TIME_MOISTURE, MOISTURE_NSAMPLE, MOISTURE_NSAMPLE_TIME)
  result <-summarise(moisture_data, TEST=filename, COUNT = n(), MEAN = mean(VALUE), SD = sd(VALUE))
  return (data.frame(result))
}

result <- analyze('shortcircuit-galvanized-wire')
result <- rbind(result,analyze('soildry-nickel-plate'))
result <- rbind(result,analyze('soildry-galvanized-wire'))
result <- rbind(result,analyze('soildry2-galvanized-wire'))
result <- rbind(result,analyze('soilwet-nickel-plate'))
result <- rbind(result,analyze('soilwet-galvanized-wire'))
result <- rbind(result,analyze('soilwet2-galvanized-wire'))
result <- rbind(result,analyze('soilwet3-galvanized-wire'))
result <- rbind(result,analyze('supersoilwet-nickel-plate'))
result <- rbind(result,analyze('supersoilwet-galvanized-wire'))
result <- rbind(result,analyze('supersoilwet2-nickel-plate'))
result <- rbind(result,analyze('supersoilwet2-galvanized-wire'))
result <- rbind(result,analyze('water-nickel-plate'))
result <- rbind(result,analyze('water-galvanized-wire'))
result <- rbind(result,analyze('water2-galvanized-wire'))
result <- rbind(result,analyze('water2-nickel-plate'))
print (result)
