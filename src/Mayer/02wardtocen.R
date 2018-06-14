library(rgdal)
library(rgeos)
library(magrittr)
library(gplots)
#Function that assigns each ward to the census tract containing its centroid and appends corresponding demographic data to the existing ward dataframe
#Population variables are scaled based on relative proportion of population between wards in a given 
#Note that wards align with census tracts often, but not always

#read in maps of wards and census tracts, reprojects census tracts to same projection as wards
ward_map<-readOGR(dsn=".","wiward",verbose=FALSE)
cen_map<-readOGR(dsn=".","wicent",verbose=FALSE) %>% 
  spTransform(ward_map@proj4string)

#read in demographic data reported at the census tract level
cen_data<-read.csv("CensusDemographicData.csv")
ward_data<-read.csv("QuickFit.csv")
ward_data<-ward_data[1:6634,]

#identify the census tract corresponding to each ward as that containing its centroid
am_in<-gCentroid(ward_map,byid=TRUE) %>%
  gContains(cen_map, ., byid=TRUE) %>%
  apply(.,1,function(x) which(x))

#match the census mapfile indices to the census demographic data csv based on GEO.id
am_in<-unlist(sapply(cen_map@data$GEOID[unlist(am_in)], function(x) which(cen_data$GEO.id2==toString(x))))

#go from ward shapefile to csv by OBJECTID_1
am_in<-unlist(sapply(ward_data$OBJECTID_1, function(x) am_in[ward_map@data$OBJECTID_1==x]))

#scale population variables by relative population sizes of wards in a particular census tract
cen_data[-c(1:3)]<-sapply(cen_data[-c(1:3)],as.numeric)
pop_in_ward<-sapply(am_in,function(x) sum(ward_data$PERSONS18[am_in==x]))
scale_pop<-ward_data$PERSONS18/pop_in_ward
cen_data[c("AA01","AA02","AA03")]<-cen_data[c("AA01","AA02","AA03")]*scale_pop

#append additional demographic data based on census tract assignment for each ward
ward_data<-cbind(ward_data, cen_data[am_in,4:ncol(cen_data)])

#convert proportions to total number based on corresponding population value, delete population columns
perc1<-c("EC02","EC03","EC04")
perc2<-c("ED01","ED02","ED03","ED04","ED05","ED06","ED07","ED08","ED09")
perc3<-c("TR04","TR05","TR06","TR07","EC05","EC06","EC07","EC08")

ward_data[perc1]<-sapply(ward_data[perc1],function(x) x*ward_data["AA01"]/100)
ward_data[perc2]<-sapply(ward_data[perc2],function(x) x*ward_data["AA02"]/100)
ward_data[perc3]<-sapply(ward_data[perc3],function(x) x*ward_data["AA03"]/100)
ward_data<-ward_data[,-which(names(ward_data)%in%c("AA01","AA02","AA03"))]

write.csv(ward_data, "QuickFitWithDemographics.csv")
