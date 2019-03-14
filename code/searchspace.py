"""
This script enumerates the complete search space of a graph given the assumption, that only nodes connected
by a path can be part of the same cluster.

.. moduleauthor:: Fabian Ball <fabian.ball@kit.edu>
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
from collections import defaultdict
import csv
import math
import os.path

from networkx import is_connected
from networkx.readwrite.graph6 import from_graph6_bytes
import pandas as pd

from datastructures import SearchSpace
from estimation import (DensityEstimator, MeanNeighborsEstimator, LbUbRatioEstimator, StirlingRatioEstimator,
                        StirlingDeltaEstimator, LbUbDeltaEstimator)


def read_graphs(path):
    graphs = []
    with open(path) as f:
        r = csv.reader(f)
        header = next(r)  # Header
        if len(header) != 2 or header[0] != 'name' or header[1] != 'graph6':
            raise Exception('Invalid file format')

        for row in r:
            name, graph6_string = row
            graph = from_graph6_bytes(bytes(graph6_string, 'ascii'))
            graph.name = name
            if is_connected(graph):
                graphs.append(graph)

    return graphs


def main():
    argparser = argparse.ArgumentParser(description='Enumerate the full searchspace for each graph in the input file.')
    argparser.add_argument('path', type=str, help='Path to a csv file of graphs in Graph6 format (rows: name,graph6)',
                           default=None)
    argparser.add_argument('--partitions', nargs='?', const=True, default=False,
                           help='Print partitions per search space level. Can only be used together '
                                'with --no_compression')
    argparser.add_argument('--no_compression', nargs='?', const=True, default=False,
                           help='Do not compress the search space level after expansion.')
    argparser.add_argument('--out', type=str, help='Path to a output folder (must exist)', default=None)
    args = argparser.parse_args()

    graphs = read_graphs(args.path)

    estimators = [MeanNeighborsEstimator(),
                  DensityEstimator(),
                  StirlingRatioEstimator(),
                  StirlingDeltaEstimator(),
                  LbUbRatioEstimator(),
                  LbUbDeltaEstimator()]

    records = []
    errors = defaultdict(float)

    for graph in graphs:
        degrees = graph.degree()
        print('Graph: {} (n={}, m={}, min_deg={}, max_deg={})'.format(graph.name,
                                                                      graph.number_of_nodes(),
                                                                      graph.number_of_edges(),
                                                                      min(degrees, key=lambda x: x[1])[1],
                                                                      max(degrees, key=lambda x: x[1])[1]))

        sp = SearchSpace(graph, compress=not args.no_compression)
        sp.build()

        sp.print_results(args.partitions)
        records.append(sp.to_record())

        for estimator in estimators:
            est = estimator.num_partitions(sp.num_nodes, sp.num_edges)
            ss = 0
            ae = 0
            print(estimator.name)
            print('Estimated number of partitions: {:.5f}'.format(est))
            for k in range(sp.num_nodes, 0, -1):
                est_k = estimator.num_partitions(sp.num_nodes, sp.num_edges, k)
                print('k={}\test #Partitions={}'.format(k, est_k))
                ss += float(est_k - sp.num_partitions(sp.num_nodes - k)) ** 2
                ae += abs((est_k - sp.num_partitions(sp.num_nodes - k)) / sp.num_partitions(sp.num_nodes - k))

            rmse = math.sqrt(ss / sp.num_nodes)
            ae = float(ae / sp.num_nodes)
            print('SS: {:.3f}'.format(ss))
            print('RMSE: {:.3f}'.format(rmse))
            print('AE: {:.3f}'.format(ae))
            errors[estimator.name] += ae
            print()

        if args.out:
            out_path = os.path.join(args.out, '{}_searchspace.csv'.format(''.join(c if c.isalnum() else '_'
                                                                                  for c in sp.graph_name)))
            pd.DataFrame.from_records(sp.levels_to_records()).to_csv(out_path, index=False)

    for name, error_sum in errors.items():
        print('Error of "{}": {:.3f}'.format(name, error_sum / len(graphs)))

    if args.out:
        out_path = os.path.join(args.out, 'graphs_searchspace.csv')
        pd.DataFrame.from_records(records).to_csv(out_path, index=False, mode='w')


if __name__ == '__main__':
    main()
