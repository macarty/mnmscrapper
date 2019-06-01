# mnmscrapper
graph analyser for a well-known social network in Spain
Yep, we did it. we're also uploading some binaries that helps to do some research backwards. Data obtained is ok for mid-May 2019.
What it does?
Well, it builds a directed graph with the votes to notes and comments between users. it is a weighted graph, so it can be regenerated using "heat" as absolute votes (I've left this on the 

It is implemented with 2 classes, one for the node itself, the second for the edge between nodes. The graph is a Python dict() of dict()s, so implements the data structure equivalent of a list of lists



Dependencies
- To generate the reverse graph I had to use BeautifulSoup library. 
- I've used also the NetworkX library, so it is required as a dependency
- Matplotlib

Case uses
- Regenerate the graph (warning, takes ages)
- Calculate the graph absolute position (no multiprocessor library used, sorry)
- Calculate top centrality, degree, betweenness and eigenvectors and plot them
- Calculate a graph of relationships using your own list

Caveats

Using the BeautifulSoup means that a change on the website CSS will make this part useless, however, anyone with enough skills and a web code analyzer can implement quickly the changes and make this thing operational

In addition to this, I've not been coding for ages. The quality of the code is definitely poor.

