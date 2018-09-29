library(dplyr)
setwd("/data/github/babilonia/research")
setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

analyze <- function(test, metal, type, filename){
  file=paste(paste("./",filename, sep=""),"csv", sep=".");
  moisture_data <- group_by(read.csv(file, head = TRUE, sep=","), 
                              SLEEP_TIME_MOISTURE, 
                              MOISTURE_NSAMPLE, 
                              MOISTURE_NSAMPLE_TIME)
  result <-summarise(TEST=test, METAL=metal, 
                    TYPE=type, moisture_data, 
                    COUNT = n(), 
                    MEAN = mean(VALUE), 
                    MEDIAN = median(VALUE),
                    MIN = min(VALUE),
                    MAX = max(VALUE),
                    SD = sd(VALUE))
  return (data.frame(result))
}

result <- analyze('shortcircuit','galvanized', 'wire', 'shortcircuit-galvanized-wire')
result <- rbind(result,analyze('soildry','nickel', 'plate', 'soildry-nickel-plate'))
result <- rbind(result,analyze('soildry','galvanized', 'wire', 'soildry-galvanized-wire'))
result <- rbind(result,analyze('soildry2','galvanized', 'wire', 'soildry2-galvanized-wire'))
result <- rbind(result,analyze('soilwet','copper', 'wire','soilwet-copper-wire'))
result <- rbind(result,analyze('soilwet','nickel', 'plate','soilwet-nickel-plate'))
result <- rbind(result,analyze('soilwet','galvanized', 'wire','soilwet-galvanized-wire'))
result <- rbind(result,analyze('soilwet2','galvanized', 'wire','soilwet2-galvanized-wire'))
result <- rbind(result,analyze('soilwet3','galvanized', 'wire','soilwet3-galvanized-wire'))
result <- rbind(result,analyze('supersoilwet','nickel', 'plate','supersoilwet-nickel-plate'))
result <- rbind(result,analyze('supersoilwet','galvanized', 'wire','supersoilwet-galvanized-wire'))
result <- rbind(result,analyze('supersoilwet2','nickel', 'plate','supersoilwet2-nickel-plate'))
result <- rbind(result,analyze('supersoilwet2','galvanized', 'wire','supersoilwet2-galvanized-wire'))
result <- rbind(result,analyze('water','nickel', 'plate','water-nickel-plate'))
result <- rbind(result,analyze('water','galvanized', 'wire','water-galvanized-wire'))
result <- rbind(result,analyze('water2','galvanized', 'wire','water2-galvanized-wire'))
result <- rbind(result,analyze('water2','nickel', 'plate','water2-nickel-plate'))
print (result)
