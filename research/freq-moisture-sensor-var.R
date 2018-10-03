library(dplyr)
library(ggplot2)
setwd("/data/github/babilonia/research")
setwd("~/Development/babilonia/research")
suppressPackageStartupMessages(library(dplyr))

multiplot <- function(plots, file, cols=1, layout=NULL) {
  library(grid)

  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}
test_label <- function (SLEEP_TIME_MOISTURE,MOISTURE_NSAMPLE,MOISTURE_NSAMPLE_TIME){
  return (paste(SLEEP_TIME_MOISTURE/1000000, "s", 
                formatC(MOISTURE_NSAMPLE, width = 3, format = "d", flag = "0"), "x",
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
    theme_bw() + ggtitle(paste(testname, testnumber, metal, type, sep='-')) + ylab("Moisture")+
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  result$data <- result_df
  result$graph  <- graph
  return (result)
}
data <- list()
result <- analyze('soilwet', 1,'galvanized', 'wire', 'freq-soilwet-galvanized-wire')
data <- rbind(data,result$data)
print (data)
multiplot(list(result$graph), cols=2)

