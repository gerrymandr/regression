
#df <- read.csv("ler.csv")

#function to compute number of wasted votes
wasted.vote <- function(x,y){
  if(x>y){
    return(x-0.5*(x+y)) #if you win, return how many extra votes you had
  } else {
    return(x) #if you lose, return how many votes you had 
    }
}

efficency.gap <- function(df){
  wasted.d.votes = Vectorize(wasted.vote)(df$Dem..Votes, df$Rep..Votes) #compute total wasted dem votes
  wasted.r.votes = Vectorize(wasted.vote)(df$Rep..Votes, df$Dem..Votes) #compute total wasted rep votes
  return(sum(wasted.d.votes-wasted.r.votes)/sum(df)) #sum the difference and divide by total number of votes
  }
  
#efficency.gap(df)
  
  
  
  
