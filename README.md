# mnmscrapper
Is a graph (as in graph theory) tool to analyse relationships within a well-known social network in Spain. This thing shows off how relations are happening on this network

Our motivation was to view existing interation within a group of users that are abusing the rest, and how the relationships are being made among them. This helped us to establish some clues about potential astroturfing, cross-voting, etc, using only public information, which is of little interest to no one, but helps explaining the group dynamics.

Yep, we did it. we're also uploading some binaries that helps to do some research backwards. Data obtained is ok for mid-May 2019.
What it does?
Well, it builds a directed graph with the votes to notes and comments between users. it is a weighted graph, so it can be regenerated using "heat" as absolute votes (I've left this on the node, as is interesting and can be used for other purposes)

It is implemented with 2 classes, one for the node itself, the second for the edge between nodes. The graph is a Python dict() of dict()s, so implements the data structure equivalent of a list of lists

The original "luserlist" has been taken from the 100 top senders, where non-active users (banned, or closed accounts) were removed.
As the graph generation takes a while, the default way is to load & restore previously scrapped information from the Website.

Note: as you can see, all the data used is PUBLIC, nicknames does not represent or references any personal data, so no GDPR concerns at all.

Dependencies
- To generate the reverse graph I had to use BeautifulSoup library. 
- NetworkX library is required as a dependency
- Matplotlib to plot graphs.

Case uses
- Regenerate the graph (warning, takes ages)
- Calculate the graph absolute position (no multiprocessor library used, sorry, so again, takes ages)
- Calculate top centrality, degree, betweenness and eigenvectors and plot them
- Calculate a graph of relationships using your own list

Caveats

Using the BeautifulSoup means that a change on the website CSS will make this part useless, however, anyone with enough skills and a web code analyzer can implement quickly the changes and make this thing operational

In addition to this, I've not been coding for ages. The quality of the code is definitely poor.

