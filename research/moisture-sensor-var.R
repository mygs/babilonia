library(dplyr)
setwd("/data/github/babilonia/research")
setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

test_label <- function (SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME){
  return (paste(SLEEP_TIME_MOISTURE/1000000, "s", 
                MOISTURE_NSAMPLE, "x",
                format(MOISTURE_NSAMPLE_TIME/1000000, digits=3, nsmall=3), "s",
                sep=""))
}
summarise_stat <- function(testname, testnumber, metal, type, filename){
  file=paste(paste("./data/",filename, sep=""),"csv", sep=".");
  moisture_data <- group_by(read.csv(file, head = TRUE, sep=","), 
                              SLEEP_TIME_MOISTURE, 
                              MOISTURE_NSAMPLE, 
                              MOISTURE_NSAMPLE_TIME)
  result <-summarise( TEST_NAME=testname,
                      TEST_NUMBER=testnumber,
                      METAL=metal, 
                      TYPE=type, 
                      moisture_data, 
                      COUNT = n(), 
                      MEAN = mean(VALUE), 
                      MEDIAN = median(VALUE),
                      MIN = min(VALUE),
                      MAX = max(VALUE),
                      SD = sd(VALUE))
  result_df <- data.frame(result)
  result_df <- mutate(result_df, TEST_ID = test_label(SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME))
  return (result_df)
}

result <- summarise_stat('shortcircuit', 1, 'galvanized', 'wire', 'shortcircuit-galvanized-wire')
result <- rbind(result,summarise_stat('soildry', 1,'nickel', 'plate', 'soildry-nickel-plate'))
result <- rbind(result,summarise_stat('soildry', 1,'galvanized', 'wire', 'soildry-galvanized-wire'))
result <- rbind(result,summarise_stat('soildry', 2,'galvanized', 'wire', 'soildry2-galvanized-wire'))
result <- rbind(result,summarise_stat('soilwet', 1,'copper', 'wire','soilwet-copper-wire'))
result <- rbind(result,summarise_stat('soilwet', 1,'nickel', 'plate','soilwet-nickel-plate'))
result <- rbind(result,summarise_stat('soilwet', 1,'galvanized', 'wire','soilwet-galvanized-wire'))
result <- rbind(result,summarise_stat('soilwet', 2,'galvanized', 'wire','soilwet2-galvanized-wire'))
result <- rbind(result,summarise_stat('soilwet', 3,'galvanized', 'wire','soilwet3-galvanized-wire'))
result <- rbind(result,summarise_stat('supersoilwet', 1,'copper', 'wire','supersoilwet-copper-wire'))
result <- rbind(result,summarise_stat('supersoilwet', 1,'nickel', 'plate','supersoilwet-nickel-plate'))
result <- rbind(result,summarise_stat('supersoilwet', 1,'galvanized', 'wire','supersoilwet-galvanized-wire'))
result <- rbind(result,summarise_stat('supersoilwet', 2,'nickel', 'plate','supersoilwet2-nickel-plate'))
result <- rbind(result,summarise_stat('supersoilwet', 2,'galvanized', 'wire','supersoilwet2-galvanized-wire'))
result <- rbind(result,summarise_stat('water', 1,'nickel', 'plate','water-nickel-plate'))
result <- rbind(result,summarise_stat('water', 1,'galvanized', 'wire','water-galvanized-wire'))
result <- rbind(result,summarise_stat('water', 2,'galvanized', 'wire','water2-galvanized-wire'))
result <- rbind(result,summarise_stat('water', 2,'nickel', 'plate','water2-nickel-plate'))
print (result)
