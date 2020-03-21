Ok. Guys. I have an idea. Maybe it’s insane. You know the sliding window function I wrote to move across target words and get the moving window? What if we did something like that (but more efficient) moving across some unit of time and constructed the full network for that moment and the surrounding moments. Then we could look a changes in the position (say even n percentile centrality scores or something) plotted over time. We might see SVOs about Jeremey Corbyn burst but still be central until x event, and so on. 
Do you see where I am going with this? Does this seem like something we could work on until it was a little less half-baked? 


This would not be a network graph. It would be graphs of measures derived from networks as they evolve over time. 


My hesitation is around network change. So perhaps it would be better to have something like changes in centrality RANK over time 


And we would need to think about how best to represent groups of SVOs that represent some property of interest. Like being about Clinton or Johnson. Perhaps something like a median and standard deviation for rank position or something? 

Do you feel confident playing with this a bit and seeing what you can do? Fine to focus on the functionality and I can come in and plaster, sand, and paint on the walls later if you like.  


*Just for some clarificaiton: are we planning on treating an entire SVO (Clinton - Brings -> BLACK MEN) as a single node in the network, with ties to other nodes containing either the same subject or object? (edited)*
*Or do we want to have each Noun be a node?*


Yeah I was thinking of computing centrality and ranking nodes from the entire directed semantic network. 
And remember we will be working with subgroups. To compare. So maybe start with a measure that doesn’t require a connected graph. Like degree even. 
Yeah, fuck it. Go with degree for now. It’s a ranked list in the end and everything is positively correlated with degree. Hahaha 
We can test it with other measures later. 


*Oh, and one final question (although I think I already know the answer to this one): at any given time point, how do we make a call about whether or not an edge exists between two nouns? My plan was to simply examine whether or not an SVO containing said nouns was bursting at any point during the period between the two time slices*

Might be good to provide an option to write the networks to disk as edge lists with an ID in the file name. And compute some descriptive statistics for the networks at each stage and write to a data structure somewhere. 