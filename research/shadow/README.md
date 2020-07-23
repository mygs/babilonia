#### SHADOW LIBRARY

https://github.com/michaeldorman/shadow


#### STL to SHP
1) Download Blender 2.83.3 https://www.blender.org/download/
2) Download https://github.com/domlysz/BlenderGIS
3) Install addons
4) Import STL in Blender
5) GIS > export (Objects: Selected Object / Mode: Objects to features / Feature: Polygon )

#### SHP to RASTER
https://stackoverflow.com/questions/35096133/converting-shapefile-to-raster
```
library(raster)
library(rgdal)
p <- shapefile('/home/msaito/Downloads/BOX.shp')
p
plot(p)
```
