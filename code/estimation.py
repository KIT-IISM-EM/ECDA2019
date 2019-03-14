"""
A module that provides different approaches to estimate the actual number of partitions of a graph.

.. moduleauthor:: Fabian Ball <fabian.ball@kit.edu>
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import abc
import math

from sympy.functions.combinatorial.numbers import stirling, binomial


def edge_decrease(n, m):
    """
    Compute the gradual expected decrease of the number of edges when
    the number of nodes is decreased by 1.
    The more dense a graph is, the more edges vanish and vice versa.

    :param n: The number of nodes of the graph before the decrease (:math:`n_{i-1}`)
    :param m: The number of edges of the graph before the decrease (:math:`m_{i-1}`)
    :return: The expected number of edges that vanish if :math:`n_i = n_{i-1} - 1`
    """
    return 2 * m / (n - 1) - 1


def estimated_num_edges(n, m, k):
    n_level = n
    m_level = m
    while n_level > k:
        n_level -= 1
        m_level -= edge_decrease(n_level + 1, m_level)
        assert m_level >= n_level - 1

    return int(math.ceil(m_level))


class PartitionNumberEstimator(object, metaclass=abc.ABCMeta):
    """
    Abstract base class of all estimators
    """
    @abc.abstractmethod
    def num_partitions(self, n, m, k=None):
        pass

    @abc.abstractproperty
    def name(self):
        pass


class MeanNeighborsEstimator(PartitionNumberEstimator):
    """
    This estimator computes the modified Stirling number for a certain k,
    but it uses the expected number of neighbors instead of the parameter k
    in the recursive definition.
    """

    @property
    def name(self):
        return 'mean_neighbors_estimator'

    def expected_num_edges(self, n, m, k):
        if not 0 < k <= n:
            return 0
        elif k == 1:
            return 0
        elif k == 2:
            return 1
        elif k == n:
            return m

        return estimated_num_edges(n, m, k)

    def expected_node_degree(self, n, m, k):
        m_k = self.expected_num_edges(n, m, k)
        return 2 * m_k / k

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(1, n + 1))

        if k in (1, n):
            return 1
        elif k == n - 1:
            return m

        return min(self.expected_node_degree(n, m, k), k) * self.num_partitions(n - 1, m, k) + \
               self.num_partitions(n - 1, m, k - 1)


class DensityEstimator(PartitionNumberEstimator):
    """
    This estimator simply weights the Stirling number for a certain k with the
    expected density of the partition induced graph.
    """

    @property
    def name(self):
        return 'density_estimator'

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(1, n + 1))

        if k in (1, n):
            return 1

        # Number of nodes of the partition induced graph
        # Estimated average number of edges of the partition induced graph
        n_level = n
        m_level = m
        while n_level > k:
            n_level -= 1
            m_level -= edge_decrease(n_level + 1, m_level)
            assert m_level >= n_level - 1

        # Maximum number of edges of the partition induced graph
        n_level_choose2 = n_level * (n_level - 1) / 2
        # Average estimated density of the partition induced graph
        rho_level = m_level / n_level_choose2

        return stirling(n, k) * rho_level


class StirlingRatioEstimator(PartitionNumberEstimator):
    @property
    def name(self):
        return 'stirling_ratio_estimator'

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(1, n + 1))

        if k in (1, n):
            return 1

        if k == n - 1:
            return m

        ratio = float(stirling(n, k) / stirling(n, k + 1))

        return ratio * self.num_partitions(n, m, k + 1)


class StirlingDeltaEstimator(PartitionNumberEstimator):
    @property
    def name(self):
        return 'stirling_delta_estimator'

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(1, n + 1))

        if k in (1, n):
            return 1

        if k == n - 1:
            return m

        delta = int(stirling(n, k) - stirling(n, k + 1))

        return self.num_partitions(n, m, k + 1) + delta


class LbUbRatioEstimator(PartitionNumberEstimator):
    @property
    def name(self):
        return 'lb_ub_ratio_estimator'

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(n, 0, -1))

        if k in (1, n):
            return 1

        if k == n - 1:
            return m

        # Recursively compute the estimate, start "from the end" (k=n, then k=n-1, ...)
        ub_k_1 = stirling(n, k + 1)  # Previous upper bound
        ub_k = stirling(n, k)  # Current upper bound
        ub_ratio = float(ub_k / ub_k_1)  # Ratio -> factor that takes the previous to the current upper bound
        lb_k_1 = binomial(n - 1, k)  # Previous lower bound
        lb_k = binomial(n - 1, k - 1)  # Current lower bound
        lb_ratio = float(lb_k / lb_k_1)  # Ratio -> factor that takes the previous to the current lower bound

        est_k_1 = self.num_partitions(n, m, k + 1)  # Previous estimation
        est_ratio = float((ub_k_1 - est_k_1) / (ub_k_1 - lb_k_1))  # Estimated linear ratio between lower/upper bound

        est_k = est_k_1 * (est_ratio * lb_ratio + (1 - est_ratio) * ub_ratio)

        return est_k


class LbUbDeltaEstimator(PartitionNumberEstimator):
    @property
    def name(self):
        return 'lb_ub_delta_estimator'

    def num_partitions(self, n, m, k=None):
        if k is None:
            return sum(self.num_partitions(n, m, i) for i in range(n, 0, -1))

        if k in (1, n):
            return 1

        if k == n - 1:
            return m

        # Recursively compute the estimate, start "from the end" (k=n, then k=n-1, ...)
        ub_k_1 = stirling(n, k + 1)  # Previous upper bound
        ub_k = stirling(n, k)  # Current upper bound
        ub_delta = int(ub_k - ub_k_1)
        lb_k_1 = binomial(n - 1, k)  # Previous lower bound
        lb_k = binomial(n - 1, k - 1)  # Current lower bound
        lb_delta = int(lb_k - lb_k_1)

        est_k_1 = self.num_partitions(n, m, k + 1)  # Previous estimation
        est_ratio = float((ub_k_1 - est_k_1) / (ub_k_1 - lb_k_1))  # Estimated linear ratio between lower/upper bound

        est_k = est_k_1 + (est_ratio * lb_delta + (1 - est_ratio) * ub_delta)

        return est_k
