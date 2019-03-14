import argparse

import matplotlib
from matplotlib import pyplot as plt
import pandas as pd
from sympy.functions.combinatorial.numbers import stirling, binomial

plt.style.use(['ggplot'])  # ggplot-like style

pgf_with_pdflatex = {
    "pgf.texsystem": "pdflatex",
    "pgf.preamble": [
         "\\usepackage{amsmath}",
         ]
}
matplotlib.rcParams.update(pgf_with_pdflatex)

matplotlib.rcParams.update({
    'font.family': 'sans',
    'figure.figsize': [4.5, 2.8],
})


def get_plot_lower_upper_bound(n):
    """
    Plot the lower and upper bound for *n* nodes.
    """
    x = list(range(1, n+1))
    lower = [binomial(n-1, k-1) for k in range(1, n+1)]
    upper = [stirling(n, k) for k in range(1, n+1)]

    fig = plt.figure()
    ax = plt.subplot('111')
    ax.plot(x, lower, label='$\\binom{n-1}{k-1}$')
    ax.plot(x, upper, label='$S(n={}, k)$'.format(n))

    ax.set_xlabel('$k$')
    ax.set_yscale('log')

    ax.legend()

    fig.tight_layout(pad=0)

    return fig


def get_plot_lb_ub_exact(df):
    """
    Plot the lower and upper bounds as well as the exact number of partitions for the given graph data.

    The dataframe *df* must contain the two columns *k* and *num_k_partitions*, where *k* is the number of
    groups to divide the *n* nodes into and *num_k_partitions* is the actual number of partitions into *k* groups.
    """
    n = df['k'].max()
    x = list(range(1, n+1))
    lower = [binomial(n-1, k-1) for k in range(1, n+1)]
    upper = [stirling(n, k) for k in range(1, n+1)]

    fig = plt.figure()
    ax = plt.subplot('111')
    ax.plot(x, lower, label='$\\binom{n-1}{k-1}$')
    ax.plot(x, upper, label='$S(n={}, k)$'.format(n))
    ax.scatter(df['k'], df['num_k_partitions'], label='Exact \# of $k$-partitions')

    ax.set_xlabel('$k$')
    ax.set_yscale('log')

    ax.legend()

    fig.tight_layout(pad=0)

    return fig


def get_plot_lower_upper_bound_const(const=50, num_plots=3):
    """
    Create a lower/upper bound plot *num_plots* times from *const* up to *const* times *num_plots*
    nodes (using *const* steps)
    """
    fig = plt.figure()
    ax = plt.subplot('111')

    for i in range(num_plots, 0, -1):
        n = i * const
        x = list(range(1, n + 1))
        lower = [binomial(n - 1, k - 1) for k in range(1, n + 1)]
        upper = [stirling(n, k) for k in range(1, n + 1)]

        lines = ax.plot(x, upper, label='$S({}, k)$'.format(n))
        ax.plot(x, lower, label='$\\binom{%s-1}{k-1}$' % n, linestyle='dashed', color=lines[0].get_color())

    ax.set_xlabel('$k$')
    ax.set_yscale('log')

    ax.legend()

    fig.tight_layout(pad=0)

    return fig


def main():
    ap = argparse.ArgumentParser(description='Script to create several different plots related to the lower and upper '
                                             'bound of the actual number of partitions of a graph. If no parameters '
                                             'are provided, upper and lower bounds for a constant number of nodes is '
                                             'shown.')
    ap.add_argument('--out', type=str, default=None,
                    help='Path to a file where the output image (pgf format) is saved. '
                         'If not provided, the plot is shown.')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--n', type=int, default=None, help='Number of nodes to plot lower and upper bound for')
    group.add_argument('--graph', type=str, default=None, help='Path to output of a graph\'s search space enumeration')

    args = ap.parse_args()

    if args.graph is not None:
        df = pd.read_csv(args.graph)
        f = get_plot_lb_ub_exact(df)
    elif args.n is not None:
        f = get_plot_lower_upper_bound(args.n)
    else:
        f = get_plot_lower_upper_bound_const()

    if args.out:
        matplotlib.use("pgf")
        f.savefig(args.out)
    else:
        plt.show()


if __name__ == '__main__':
    main()
