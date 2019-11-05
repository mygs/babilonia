library(psych)


setwd("~/Development/babilonia/research/mux-capacitive")

data <- read.csv("./air00001.csv", head = TRUE, sep=",")

#head(data)
summary(data)
describe(data)

boxplot(data$MUX0,data$MUX1,data$MUX2,data$MUX3,
        main="Boxplot comparing Analogic ports",
        col= rainbow(4),
        horizontal = TRUE)

hist(data$MUX0,col='skyblue')
hist(data$MUX6,add=T, col='red')
