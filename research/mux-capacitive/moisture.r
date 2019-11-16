library(psych)
library(ggplot2)
library(lmtest)
library(fpp2)

#setwd("~/Development/babilonia/research/mux-capacitive")

data <- read.csv("./test0001.csv", head = TRUE, sep=",")
#head(data)
#summary(data)
describe(data)

#plot.ts(data)
#boxplot(data$MUX0,data$MUX1,data$MUX2,data$MUX3, main="Boxplot comparing Analogic ports",col= rainbow(4),horizontal = TRUE)
#hist(data$MUX0,col='skyblue')
#hist(data$MUX6,add=T, col='red')
#ggplot(data=data, mapping=aes(TIMESTAMP, MUX3)) + geom_line()
#acf(data)
mux <-data$MUX2
plot(mux)
sm <- ma(mux,order=1800)
lines(sm,col="red")

acf(sm, lag.max=34)


fitARIMA <- arima(mux0, order=c(1,1,1),seasonal = list(order = c(1,0,0), period = 12),method="ML")
coeftest(fitARIMA) 

#Random walk ARIMA(0,1,0)