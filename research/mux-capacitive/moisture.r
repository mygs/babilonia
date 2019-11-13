library(psych)
library(ggplot2)
library(lmtest)
library(fpp2)


setwd("~/Development/babilonia/research/mux-capacitive")

data <- read.csv("./test0002.csv", head = TRUE, sep=",")
options(tz="America/Sao_Paulo")
#head(data)
#summary(data)
describe(data)

#plot.ts(data)
#boxplot(data$MUX0,data$MUX1,data$MUX2,data$MUX3, main="Boxplot comparing Analogic ports",col= rainbow(4),horizontal = TRUE)
#hist(data$MUX0,col='skyblue')
#hist(data$MUX6,add=T, col='red')
#ggplot(data=data, mapping=aes(TIMESTAMP, MUX3)) + geom_line()
#acf(data)
mux0 <-data$MUX0
plot(mux0)
sm <- ma(mux0,order=12)
lines(sm,col="red")
mux0.plot()
acf(data$MUX0, lag.max=34)


fitARIMA <- arima(mux0, order=c(1,1,1),seasonal = list(order = c(1,0,0), period = 12),method="ML")
coeftest(fitARIMA) 

#Random walk ARIMA(0,1,0)