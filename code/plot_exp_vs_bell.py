import argparse

import matplotlib
from matplotlib import pyplot as plt
import pandas as pd
from sympy.functions.combinatorial.numbers import bell

plt.style.use(['ggplot'])  # ggplot-like style

matplotlib.rcParams.update({
    'font.family': 'sans',
    'figure.figsize': [4.5, 2.8],
})


def get_plot_lower_upper_bound(max_n):
    """
    Plot the lower and upper bound on a log-scaled y axis for 1 to *max_n* nodes.
    """
    x = list(range(1, max_n + 1))
    lower = [2 ** (i - 1) for i in range(1, max_n + 1)]
    upper = [bell(i) for i in range(1, max_n + 1)]

    fig = plt.figure()
    ax = plt.subplot('111')
    ax.plot(x, lower, label='$2^{n-1}$')
    ax.plot(x, upper, label='$B(n)$')

    ax.set_xlabel('$n$')
    ax.set_yscale('log')

    ax.legend()

    fig.tight_layout(pad=0)

    return fig


def get_plot_lb_ub_graphs_density(df):
    """
    Plot all graphs in the dataframe *df* (columns *n*, *m*, *num_partitions* needed) at their designated
    position in the plot of lower and upper bound of the number of partitions.
    Each data point that corresponds to a graph is weighted by the graph's normalized density.
    """
    max_n = df['n'].max()
    df['n_density'] = (2 * df['m'] / (df['n'] - 1) - 2) / (df['n'] - 2)
    df['n_density'].fillna(1, inplace=True)

    x = list(range(1, max_n + 1))
    lower = [2 ** (i - 1) for i in range(1, max_n + 1)]
    upper = [bell(i) for i in range(1, max_n + 1)]

    fig = plt.figure()
    ax = plt.subplot('111')
    ax.plot(x, lower, label='$2^{n-1}$')
    ax.plot(x, upper, label='$B(n)$')

    col = plt.rcParams['axes.prop_cycle'].by_key()['color'][2]

    for row in df.iterrows():
        pt = ax.scatter(row[1]['n'], row[1]['num_partitions'],
                        marker='o',
                        color=col,
                        s=10 + 90 * row[1]['n_density']
                        )

    # Simply add label to the last added point to make it appear in the legend
    pt.set_label('Actual \# of partitions, weighted by density')

    ax.set_yscale('log')
    ax.legend()

    fig.tight_layout(pad=0)

    return fig


def main():
    ap = argparse.ArgumentParser(description='Create a plot of the lower and upper bound of the number of partitions '
                                             'of n nodes. If a csv file of graph data is provided, additionally plot '
                                             'the actual number of partitions per graph, visualized in dependence of '
                                             'the graph\'s density.')
    ap.add_argument('--out', type=str, default=None,
                    help='Path to a file where the output image (pgf format) is saved. '
                         'If not provided, the plot is shown.')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--n', type=int, default=10, help='Number of nodes to plot lower and upper bound for')
    group.add_argument('--graphs', type=str, default=None,
                       help='Path to a csv file of graph data. The columns *n*, *m*, and *num_partitions* must exist.')

    args = ap.parse_args()

    if args.graphs:
        df = pd.read_csv(args.graphs)
        f = get_plot_lb_ub_graphs_density(df)
    else:
        f = get_plot_lower_upper_bound(args.n)

    if args.out:
        matplotlib.use("pgf")
        f.savefig(args.out)
    else:
        plt.show()


if __name__ == '__main__':
    main()
