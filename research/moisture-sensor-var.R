library(dplyr)
setwd("/data/github/babilonia/research")
#setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

analyze <- function(filename){
#  print('===========================================================================')
  file=paste(paste("./",filename, sep=""),"csv", sep=".");
  print(toupper(filename))
  moisture_data <- read.csv(file, head = TRUE, sep=",");
  moisture_data <- group_by(moisture_data, SLEEP_TIME_MOISTURE, MOISTURE_NSAMPLE, MOISTURE_NSAMPLE_TIME)
  summarise(moisture_data, TEST=filename, COUNT = n(), MEAN = mean(VALUE), SD = sd(VALUE))
}


analyze('shortcircuit-galvanized-wire')
analyze('soildry-nickel-plate')
analyze('soildry-galvanized-wire')
analyze('soilwet-nickel-plate')
analyze('soilwet-galvanized-wire')
analyze('soilwet2-galvanized-wire')
analyze('supersoilwet-nickel-plate')
analyze('supersoilwet-galvanized-wire')
analyze('supersoilwet2-nickel-plate')
analyze('supersoilwet2-galvanized-wire')
analyze('water-nickel-plate')
analyze('water-galvanized-wire')
analyze('water2-nickel-plate')
