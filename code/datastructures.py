"""
Naive data structures that allow complete search space enumeration for SMALL graphs.
The only assumption that underlies the search space is that only nodes/clusters connected by an
edge can be merged.

.. moduleauthor:: Fabian Ball <fabian.ball@kit.edu>
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from networkx import Graph
from sympy.functions.combinatorial.numbers import bell, stirling, binomial


class fset(frozenset):
    def __str__(self):
        return '{%s}' % (','.join(map(str, self)),)

    # We need comparison!
    def __lt__(self, y):
        if min(self) < min(y):
            return True
        elif min(self) > min(y):
            return False
        else:  # Mins are equal
            x_sorted = sorted(self)
            y_sorted = sorted(y)

            for idx, el in enumerate(x_sorted):
                if idx >= len(y_sorted):  # Prefixes are equal, x is longer => y is smaller
                    return False

                if el < y_sorted[idx]:
                    return True
                elif el > y_sorted[idx]:
                    return False

            if len(x_sorted) < len(y_sorted):  # Prefixes are equal, y is longer => x is smaller
                return True
            else:  # Lengths are equal, sorted elements as well => x == y
                return False

    def __gt__(self, other):
        return not self < other and not self == other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


def freeze(x):
    try:
        return fset(x)
    except TypeError:
        return fset([x])


class SearchSpaceNode(object):
    def __init__(self, g):
        # Create a new graph with 'frozen' nodes (i.e. the nodes are frozensets)
        self._graph = Graph()
        for edge in g.edges:
            s, t = sorted(edge)
            self._graph.add_edge(freeze(s), freeze(t))
        for node in g.nodes:
            self._graph.add_node(freeze(node))

    def __hash__(self):
        # This only takes edges into account, no other attributes (e.g. weights)!
        # IMPORTANT: Sorting, as we use frozen sets as nodes
        return hash(tuple(sorted(tuple(tuple(sorted(e)) for e in self._graph.edges))))

    def __eq__(self, other):
        return self.graph.edges == other.graph.edges

    @property
    def graph(self):
        return self._graph

    def expand(self):
        """
        This generates all the partitions that result from merging two existing clusters connected by an edge.
        """
        for edge in self._graph.edges:
            new_graph = Graph()
            s, t = edge  # The edge that connects two nodes to be joined

            new_node = s.union(t)  # Create the new node

            new_graph.add_node(new_node)  # Add the new node, as possibly no edges remain

            for e in self._graph.edges:
                if edge == e:
                    continue

                a, b = e
                if a in edge:
                    new_graph.add_edge(new_node, b)
                elif b in edge:
                    new_graph.add_edge(a, new_node)
                else:  # Just add the existing edge
                    new_graph.add_edge(*e)

            assert new_graph.order() == self._graph.order() - 1

            yield SearchSpaceNode(new_graph)

    def __str__(self):
        return '|'.join(map(str, sorted(self._graph.nodes)))


class SearchSpaceLevel(object):
    _next = None
    _previous = None
    _level = 0
    _num_partitions = None

    def __init__(self, graph=None, previous=None):
        if graph and previous:
            raise ValueError('Only one of graph and previous allowed')
        elif not graph and not previous:
            raise ValueError('Either graph or previous needed')

        self._nodes = set()

        if graph:
            self._nodes.add(SearchSpaceNode(graph))
        elif previous:
            self._previous = previous
            self._level = previous.level + 1

    @property
    def level(self):
        return self._level

    @property
    def num_partitions(self):
        if self._num_partitions is not None:
            return self._num_partitions
        else:
            return len(self._nodes)

    @property
    def nodes(self):
        return self._nodes

    def add_node(self, node):
        self._nodes.add(node)

    def expand(self):
        if self._next:
            raise ValueError('Already expanded')

        self._next = SearchSpaceLevel(previous=self)

        for node in self._nodes:
            for new_node in node.expand():
                self._next.add_node(new_node)  # Set property assures no duplicate nodes

        return self._next

    def compress(self):
        """
        Discard the list of search space nodes (=partitions) and only keep the number of nodes.
        :return:
        """
        if self._nodes is not None:
            self._num_partitions = len(self._nodes)
            self._nodes = None

    def mean_num_edges(self):
        if self._nodes is None:
            raise ValueError('The search space is compressed, computation impossible')
        return sum(n.graph.number_of_edges() for n in self._nodes) / len(self.nodes)


class SearchSpace(object):
    _levels = None

    def __init__(self, graph, compress=True):
        """
        Create the search space for the given *graph*. If *compress* is True, each level in the search
        space will be compressed after it was expanded. This means the actual partitions are deleted and
        only the number of partitions in this level is saved.
        """
        self._graph = graph
        self._compress = compress

    def build(self):
        """
        Iteratively build the search space. Call this method only once!
        """
        first_level = SearchSpaceLevel(graph=self._graph)
        second_level = first_level.expand()
        self._levels = [first_level, second_level]

        if self._compress:
            first_level.compress()

        while self._levels[-1].num_partitions > 1:
            self._levels.append(self._levels[-1].expand())

            if self._compress:
                self._levels[-2].compress()

        if self._compress:
            self._levels[-1].compress()

        return self._levels

    @property
    def graph_name(self):
        return self._graph.name

    @property
    def num_nodes(self):
        return self._graph.order()

    @property
    def num_edges(self):
        return self._graph.size()

    @property
    def levels(self):
        return self._levels

    @property
    def num_levels(self):
        return len(self._levels)

    def bell(self):
        return int(bell(self.num_nodes))

    def num_partitions_ub(self):
        """
        Get the exact absolute upper bound for the number of partitions.
        This is just the Bell number on the number of nodes.

        :return:
        """
        return self.bell()

    def num_partitions_lb(self):
        """
        Get the exact absolute lower bound for the number of partitions.
        This is just the number of partitions of a tree of :math:`n` nodes: :math:`2^{n-1}`.

        :return:
        """
        return 2 ** (self.num_nodes - 1)

    def num_partitions(self, level=None):
        if level is None:
            return sum(level.num_partitions for level in self.levels)
        else:
            return self.levels[level].num_partitions

    def stirling(self, level):
        return int(stirling(self.num_nodes, self.num_nodes - level))

    def num_k_partitions_ub(self, level):
        """
        Get the exact upper bound for the number of :math:`k` partitions.
        This is :math:`S(n, k)` with :math:`k=n-l`; :math:`l` is the level.

        :param level:
        :return:
        """
        return self.stirling(level)

    def num_k_partitions_lb(self, level):
        """
        Get the lower bound for the number of :math:`k` partitions.
        This is :math:`\binom{n-1}{k-1}` with :math:`k=n-l`; :math:`l` is the level.

        :param level:
        :return:
        """
        return binomial(self.num_nodes - 1, self.num_nodes - level - 1)

    def print_results(self, print_nodes=False):
        print('Bell number = {}'.format(self.bell()))
        print('Actual number of partitions = {}'.format(self.num_partitions()))

        for level in self.levels:
            print('Level {lev} (k={k},\tS(n, k)={st}):\texact #Partitions={p}'.format(lev=level.level,
                                                                                      p=level.num_partitions,
                                                                                      st=self.stirling(level.level),
                                                                                      k=self.num_nodes - level.level
                                                                                      )
                  )
            if level.nodes and print_nodes:
                print('\t'.join(map(str, level.nodes)))
        print()

    def to_record(self):
        """
        Get a record of the search space of the graph
        :return:
        """
        return {'name': self.graph_name,
                'n': self.num_nodes,
                'm': self.num_edges,
                'num_partitions_ub': self.num_partitions_ub(),
                'num_partitions_lb': self.num_partitions_lb(),
                'num_partitions': self.num_partitions()
                }

    def levels_to_records(self):
        """
        Get a list of records for each level in the search space individually
        :return:
        """
        records = []

        for level in self.levels:
            records.append({'level': level.level,
                            'k': self.num_nodes - level.level,
                            'num_k_partitions_ub': self.num_k_partitions_ub(level.level),
                            'num_k_partitions_lb': self.num_k_partitions_lb(level.level),
                            'num_k_partitions': self.num_partitions(level.level)
                            })

        return records
