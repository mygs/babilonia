library(dplyr)
library(ggplot2)
setwd("/data/github/babilonia/research")
setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

test_label <- function (SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME){
  return (paste(SLEEP_TIME_MOISTURE/1000000, "s", 
                MOISTURE_NSAMPLE, "x",
                format(MOISTURE_NSAMPLE_TIME/1000000, digits=3, nsmall=3), "s",
                sep=""))
}
analyze <- function(testname, testnumber, metal, type, filename){
  result <- list()
  file=paste(paste("./data/",filename, sep=""),"csv", sep=".");
  moisture_data <- group_by(read.csv(file, head = TRUE, sep=","), 
                              SLEEP_TIME_MOISTURE, 
                              MOISTURE_NSAMPLE, 
                              MOISTURE_NSAMPLE_TIME)
  result_summarise <-summarise( TEST_NAME=testname,
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
  result_df <- data.frame(result_summarise)
  result_df <- mutate(result_df, TEST_ID = test_label(SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME))
  
  graph <- ggplot(result_df,  aes(x = TEST_ID,  y = MEAN)) +
    geom_errorbar(aes(ymin = MEAN-SD, ymax =  MEAN+SD), width = 0.05,  size  = 0.5) +
    geom_point(shape = 15,  size  = 4) +
    theme_bw() + ggtitle(paste(testname, metal, type, sep='-')) + ylab("Moisture")
  result$data <- result_df
  result$graph  <- graph
  return (result)
}

result <- analyze('shortcircuit', 1, 'galvanized', 'wire', 'shortcircuit-galvanized-wire')$data



result <- rbind(result,analyze('soildry', 1,'nickel', 'plate', 'soildry-nickel-plate')$data)
result <- rbind(result,analyze('soildry', 1,'galvanized', 'wire', 'soildry-galvanized-wire')$data)
result <- rbind(result,analyze('soildry', 2,'galvanized', 'wire', 'soildry2-galvanized-wire')$data)
result <- rbind(result,analyze('soilwet', 1,'copper', 'wire','soilwet-copper-wire')$data)
result <- rbind(result,analyze('soilwet', 1,'nickel', 'plate','soilwet-nickel-plate')$data)
result <- rbind(result,analyze('soilwet', 1,'galvanized', 'wire','soilwet-galvanized-wire')$data)
result <- rbind(result,analyze('soilwet', 2,'galvanized', 'wire','soilwet2-galvanized-wire')$data)
result <- rbind(result,analyze('soilwet', 3,'galvanized', 'wire','soilwet3-galvanized-wire')$data)
result <- rbind(result,analyze('supersoilwet', 1,'copper', 'wire','supersoilwet-copper-wire')$data)
result <- rbind(result,analyze('supersoilwet', 1,'nickel', 'plate','supersoilwet-nickel-plate')$data)
result <- rbind(result,analyze('supersoilwet', 1,'galvanized', 'wire','supersoilwet-galvanized-wire')$data)
result <- rbind(result,analyze('supersoilwet', 2,'nickel', 'plate','supersoilwet2-nickel-plate')$data)
result <- rbind(result,analyze('supersoilwet', 2,'galvanized', 'wire','supersoilwet2-galvanized-wire')$data)
result <- rbind(result,analyze('water', 1,'nickel', 'plate','water-nickel-plate')$data)
result <- rbind(result,analyze('water', 1,'galvanized', 'wire','water-galvanized-wire')$data)
result <- rbind(result,analyze('water', 2,'galvanized', 'wire','water2-galvanized-wire')$data)
result <- rbind(result,analyze('water', 2,'nickel', 'plate','water2-nickel-plate')$data)
print (result)
