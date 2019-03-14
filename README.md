# ECDA2019

This repository contains the slides and additional material of the talk "Bounds for the Number of Partitions of a Graph
" by Fabian Ball and Andreas Geyer-Schulz that was held at the European Conference on Data Analysis on Match 19, 2019 in Bayreuth, Germany.

## talk/
Just the slides of the talk.

### Abstract
We know from combinatorics that the number of partitions of a set of $n$ elements is given by the 
Bell number $B(n)$. This number increases rapidly, even for smaller $n$. The Bell number can be 
written as the sum of the Stirling numbers of the second kind, $S(n, k)$, over all $k=1$ to $n-1$.
$S(n, k)$ determines the number of partitions of an $n$-element set into $k$ non-empty parts.
However, in graph clustering we are interested in a 'good' partition, which, independent of the
used algorithm, normally depends on the adjacency of the graph. This means in particular that
each cluster of a graph partition contains only nodes which are connected. The constraint highly
restricts the number of possible partitions.

Our contribution provides examples of the possible partitions of very small graphs ($n \leq 13$ nodes).
Furthermore, we propose an estimate upper bound of the actual number of partitions, which is based on
the number of edges, and present the exact number of possible partitions of trees.
Trees are the sparsest possible connected graphs and, therefore, the number of tree partitions is a lower bound.
This lower bound is $2^m$ and thus still exponential.

## code/
This folder contains several Python scripts. Run them with Python3 (some of them are also compatible with Python2).
You will need the following external libraries (not every script needs every one, if you want to differentiate, have a look at the beginning of each script):
* `future`
* `networkx`
* `sympy`
* `pandas`
* `requests`
* `beautifulsoup4`
* `matplotlib`

The scripts can be executed in the following logical order:
1. `download_smallgraphs.py`: This wil download the small graphs from http://www.graphclasses.org/smallgraphs.html
1. `searchspace.py`: Enumerate the searchspaces of the small graphs
1. `plot_exp_vs_bell.py`: Create plots that relate the upper and lower bound of the total number of partitions of a graph
1. `plot_lb_vs_Snk.py`: Create plots that relate the upper and lower bound of the number of k-partitions of a graph

All scripts can be executed as `python3 <scriptname> -h` to get some information on how to call them.
The files `estimation.py` and `datastructures.py` contain code that is used by `searchspace.py`.

The code is not intended to be used in a production environment!

## data/
This folder contains data that are the result of some of the above scripts. 

All files prefixed `input_` can be used as input for `searchspace.py`.`input_smallgraphs.csv` is the result of downloading the small graphs with `download_smallgraphs.py`.

`searchspace_sizes_all_graphs.csv` contains the exact number of partitions of all small graphs, whereas the subfolder `searchspace_sizes_graphs` does contain the exact numbers of k-partitions for each graph individually. The former file can be used as input for `plot_exp_vs_bell.py`; the latter files can be used as input for `plot_lb_vs_Snk.py`.

## Reference
> Ball, Fabian. 2019. “Bounds for the Number of Partitions of a Graph.” Talk presented at the European Conference on Data Analysis 2019, Bayreuth, March 18. http://www.gfkl.org/ecda2019/.
