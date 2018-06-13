library(rgdal)
library(rgeos)
library(magrittr)

#Function that assigns each ward to the census tract containing its centroid and appends corresponding demographic data to the existing ward dataframe
#Note that wards allign with census tracts often, but not always

#read in maps of wards and census tracts, reprojects census tracts to same projection as wards
ward_map<-readOGR(dsn=".","wiward",verbose=FALSE)
cen_map<-readOGR(dsn=".","wicent",verbose=FALSE) %>% 
  spTransform(ward_map@proj4string)

#read in demographic data reported at the census tract level
cen_data<-read.csv("CensusDemographicData.csv")

#identify the census tract corresponding to each ward as that containing its centroid
am_in<-gCentroid(ward_map,byid=TRUE) %>%
  gContains(cen_map, ., byid=TRUE) %>%
  apply(.,1,function(x) which(x))

#manually assign ward split by water to the correct census tract (its centroid is in Lake Michigan)
am_in[5984]<-594

#match the census mapfile indices to the census demographic data csv baased on GEO.id
am_in<-unlist(sapply(cen_map@data$GEO_ID[unlist(am_in)], function(x) which(cen_data$GEO.id==toString(x))))
#append additional demographic data based on census tract assignment for each ward
ward_newdata<-ward_map
ward_newdata@data<-cbind(ward_map@data, cen_data[am_in,4:ncol(cen_data)])
writeOGR(ward_newdata, dsn=".","WardMoreDemographics")
