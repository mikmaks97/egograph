# egograph
My Facebook egograph with maximal and maximum clique analyses

![graph](maximum_cliques.png)

[Complementary presentation on cliques](https://docs.google.com/presentation/d/1VTfan6KJfcmNoz7mxHmQKX_tO1Im1w2Nf5rgLHJrey4/edit?usp=sharing)

## Generating your own egograph
`fb_scrape.py` is a script that uses Selenium webdriver to scrape mutual friend names and saves them as vertex info
to a text file. Friends who are friends with each other are saved as edges to another text file. This script is slow
and may be outdated, especially with Facebook's graph API, so use at your own discretion.

`graph.py` draws a graph using vertex and edge data from the above text files. It has implementations of the Bron-Kerbosch
and Tomita maximal clique detection algorithms and the intelligent backtracking algorithm for maximum clique
enumeration.

## Further work
A temporal analysis + visualization of graph change over time as new friendships are started and old ones are stopped
(friend addition and deletion) and how that affects the neighborhoods would be interesting.

## References
Conte, Alessio. “Review of the Bron-Kerbosch algorithm and variations.”
    www.dcs.gla.ac.uk/~pat/jchoco/clique/enumeration/report.pdf.

Eblen, John D., et al. “The Maximum Clique Enumeration Problem: Algorithms, Applications and Implementations.”
    Bioinformatics Research and Applications Lecture Notes in Computer Science, vol. 13, no. 10, 25 June 2012, p
    p. 306–319., doi:10.1007/978-3-642-21260-4_30.

