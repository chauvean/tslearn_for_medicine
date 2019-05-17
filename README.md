# tslearn_for_medicine

Raw input : 
array of values transformed in tslearn compatible time  serie. 
ex : bla++, bla-, blast+, bla++ etc...

Barycenters.py :

classic barycenter of time series. Euclidean, petitjean or dtw way.
ndarray.shape : dimensions of x, y, z ... axis ( ex: ndarray.shape=(2,3) array of size 2*3).

We have dicrete values (++, + ...) So the evaluation will be with float. Take the round to come back to our initial format
(takes into account the most powerful evaluation, worst case scenario).

USE : 
If we want to have a global idea of the behavior of our samples. 
This uses local analysis as barycenter is done dimension by dimension.
( --,-,N,+,++ mapped to 0,1,2,3,4
Ex : eval_1 = [ 1, 2, 1, 4, 0] eval_2 = [ 1,2,1, 3, 2]
return : [ 1,2,1, 3, 1] : locally 1,2,1 is the right behavior. 

Problem : with a lot of samples we can't know which part are the most relevant.
A defined mean evaluation could have been done by the same values or by random instances averaging to this value 
(1 done by (1,1,1) or (0,0,3));

Therefore I added variance_array function. It evaluates the variance between all the values compared to each other.
If the variance is superior to a certain treshold we consider the value the value irrelevant.
example : 

ts1 = [1, 1, 1, 0, 3, 0, 1]
ts2 = [1, 1, 1, 2, 4, 3, 1]
bary : [1 ,1 ,1 ,1 ,3.5 ,1.5 ,1 ]
variances : [0.   0.   0.   1.   0.25 2.25 0.  ]
relevant values : [1.0, 1.0, 1.0, -1, -1, -1, 1.0]
We filter here only the values with variance < treshold.  


Use of Bollinger stripes : 
Calculate time-serie of means of values at a given time. Draw lines of variances above and below the mean one.
(volatility is 2-3 times variance.
Mean increasing with small volatility. Value of our samples are increasing and globally all together. 
Mean and volatility more or less constant or with small rates, nothing interesting (if inferior to treshold ?)

--> This representation will help to evaluate potential rise in our values, the volatility helping to know wether
the rise is relevant or not.

What could be added towards our study :
Treshold for volatility and blast value. If first under treshold, we can identify common patterns happening after tzero.
If it is significantly over treshold,  not that useful to recognise patterns. If blast over treshold we still can identify odd values,
moreover if volatility small (below treshold), we know that a real problem happening over most patients  



clustering.py : 

Silouhette coefficients : "Evaluation of how well sample classified to its own cluster" (from file doc)
clustering made.
From time series, calculate clustering. For each cluster, calculate coeffs. If most have high coeffs, "preserve" it.
Calculating coeffs, then compare them to a treshold to evaluate if classification is efficient.

From an iteration to another We preserve clusters with their contains who have "most" of their samples having a high silouhette value. 
Then we redo a k-means clustering on the remaining samples.

We add a max number of iterations. Classification stops if nb iterations exceeded or if nb clusters and their size variations 
stays below treshold.

--> See code on my other computer 


I am currently implementing a dictionnary solution. The keys are the possible combinations happening at a defined datefrom and value is the corresponding output. For instance with n=2 we have 2-sized combinations mapped to their output combination. Ex : A->B C->D in the dic A,C mapped to B,D. 
For m-length precedence relationships we will search for matching outputs-inputs of different values. 

The problem is that there are too many combinations. (sum over k ( n parmi length_of_date_k ))














