"""
A simple download script to get all the small graphs from http://www.graphclasses.org/smallgraphs.html

The result is the file 'smallgraphs.csv', which consists of two columns: name, graph6
The name is in LaTeX math format as used in the website and the second column contains
the graph data encoded in Graph6 format (see http://cs.anu.edu.au/~bdm/data/formats.html).

E.g. NetworkX can handle this format:
https://networkx.github.io/documentation/stable/reference/readwrite/sparsegraph6.html

.. moduleauthor:: Fabian Ball <fabian.ball@kit.edu>
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import csv

import bs4
import requests


def _parse_name(soup_node):
    if not soup_node.name:
        tokens = soup_node.split('=')  # Maybe we have more than one name
        return ' = '.join(t.replace('\u222a', '\cup').strip() for t in tokens)
    elif soup_node.name == 'sub':
        return '_{%s}' % ''.join(_parse_name(c) for c in soup_node.children)
    elif 'complement' in soup_node.get('class', []):
        return '\overline{%s}' % ''.join(_parse_name(c) for c in soup_node.children)
    else:
        raise ValueError(soup_node)


def _parse_graph(soup_node):
    children = list(soup_node.children)
    name_parts = children[:-1]
    graph_part = children[-1]
    assert 'class' in graph_part.attrs and 'graph6' in graph_part.get('class')

    name = ''.join(_parse_name(name_part) for name_part in name_parts)

    return name, graph_part.text.strip()


def get_small_graphs_online():
    r = requests.get('http://www.graphclasses.org/smallgraphs.html')
    soup = bs4.BeautifulSoup(r.content, 'lxml')

    graphs = []

    for span in soup.find_all('span', class_='graph6'):
        name, graph6_string = _parse_graph(span.parent)
        graphs.append((name, graph6_string))

    return graphs


def write_csv(graphs):
    with open('smallgraphs.csv', mode='w+') as f:
        w = csv.writer(f)
        w.writerow(('name', 'graph6'))
        for graph in graphs:
            try:
                w.writerow(graph)
            except:
                print(graph)
                raise


if __name__ == '__main__':
    write_csv(get_small_graphs_online())
