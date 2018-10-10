library(ggplot2)

# HEADER: TIMESTAMP,VALUE
MOISTURE <- read.csv("./data/copper-wire.csv", head = TRUE, sep=",")
#plot(MOISTURE)
ggplot(data = MOISTURE, aes(x = TIMESTAMP, y = VALUE))+
        geom_line(color="#00AFBB")+
        stat_smooth(color ="#FC4E07",fill = "#FC4E07", method = "loess")