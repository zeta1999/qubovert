#   Copyright 2019 Joseph T. Iosue
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""_vertex_cover.py.

Contains the VertexCover class. See ``help(qubovert.problems.VertexCover)``.

"""

# from qubovert.utils import QUBOMatrix
from qubovert import HOBO
from qubovert.problems import Problem


__all__ = 'VertexCover',


class VertexCover(Problem):
    """VertexCover.

    Class to manage converting Vertex Cover to and from its QUBO and
    Ising formluations. Based on the paper hereforth designated [Lucas]_.

    The goal of the VertexCover problem is to find the smallest number of
    verticies that can be colored such that every edge of the graph is
    incident to a colored vertex.

    VertexCover inherits some methods and attributes from the Problem class.
    See ``help(qubovert.problems.Problem)``.

    Example usage
    -------------
    >>> from qubovert.problems import VertexCover
    >>> from any_module import qubo_solver
    >>> # or you can use my bruteforce solver...
    >>> # from qubovert.utils import solve_qubo_bruteforce as qubo_solver
    >>> edges = {("a", "b"), ("a", "c"), ("c", "d"), ("a", "d")}
    >>> problem = VertexCover(edges)
    >>> Q  = problem.to_qubo()
    >>> obj, sol = qubo_solver(Q)
    >>> solution = problem.convert_solution(sol)

    >>> print(solution)
    {"a", "c"}

    >>> print(problem.is_solution_valid(solution))
    True  # since each edge is adjacent to either "a" or "c".

    >>> print(obj == len(solution))
    True

    References
    ----------
    .. [Lucas] Andrew Lucas. Ising formulations of many np problems. Frontiers
        in Physics, 2:5, 2014.

    """

    def __init__(self, edges):
        """__init__.

        The goal of the VertexCover problem is to find the smallest number of
        verticies that can be coloredsuch that every edge of the graph is
        incident to a colored vertex.  All naming conventions follow the names
        in the paper [Lucas].

        Parameters
        ----------
        edges : set of two element tuples.
            Describes edges of the graph.

        Examples
        -------
        >>> edges = {("a", "b"), ("a", "c")}
        >>> problem = VertexCover(edges)

        >>> edges = {(0, 1), (0, 2)}
        >>> problem = VertexCover(edges)

        """
        self._edges = edges.copy()
        self._vertices = {y for x in edges for y in x}
        self._vertex_to_index = {x: i for i, x in enumerate(self._vertices)}
        self._index_to_vertex = {i: x for x, i in
                                 self._vertex_to_index.items()}
        self._N, self._n = len(self._vertices), len(self._edges)

    @property
    def E(self):
        """E.

        A copy of the set of edges of the graph. Updating the copy will not
        update the instance set.

        Return
        -------
        E : set of two element tuples.
            A copy of the edge set defining the Vertex Cover problem.

        """
        return self._edges.copy()

    @property
    def V(self):
        """V.

        A copy of the vertex set of the graph. Updating the copy will not
        update the instance set.

        Return
        -------
        V : set.
            A copy of the set of vertices corresponding to the edge set for the
            Vertex Cover problem.

        """
        return self._vertices.copy()

    @property
    def num_binary_variables(self):
        """num_binary_variables.

        The number of binary variables that the QUBO and Ising use.

        Return
        -------
        num : integer.
            The number of variables in the QUBO/Ising formulation.

        """
        return self._N

    def to_qubo(self, A=2, B=1):
        r"""to_qubo.

        Create and return the vertex cover problem in QUBO form following
        section 4.3 of [Lucas]. The Q matrix for the QUBO
        will be returned as an uppertriangular dictionary. Thus, the problem
        becomes minimizing :math:`\sum_{i \leq j} x_i x_j Q_{ij}`. ``A`` and
        ``B`` are parameters to enforce constraints.

        It is formatted such that if all the constraints are satisfied, then
        the objective function will be equal to the total number of colored
        verticies.

        Parameters
        ----------
        A: positive float (optional, defaults to 2).
            A enforces the constraints. See section 4.3 of [Lucas].
        B: positive float that is less than A (optional, defaults to 1).
            See section 4.3 of [Lucas].

        Return
        -------
        Q : qubovert.utils.QUBOMatrix object.
            The upper triangular QUBO matrix, a QUBOMatrix object.
            For most practical purposes, you can use QUBOMatrix in the
            same way as an ordinary dictionary. For more information,
            see help(qubovert.utils.QUBOMatrix).

        Example
        -------
        >>> problem = VertexCover({(0, 1), (0, 2)})
        >>> Q = problem.to_qubo()

        """
        # all naming conventions follow the paper listed in the docstring

#        Q = QUBOMatrix()
#
#        # encode H_B (equation 34)
#        for i in range(self._N):
#            Q[(i,)] += B
#
#        # encode H_A, ie each edge is adjacent to at least one colored vertex.
#        # we don't use HOBO().to_qubo because we want to keep our mapping.
#        for u, v in self._edges:
#            iu, iv = self._vertex_to_index[u], self._vertex_to_index[v]
#            Q += HOBO().OR(iu, iv, lam=A)
#
#        return Q

        H = HOBO()
        H.set_mapping(self._vertex_to_index)

        # encode H_B (equation 34)
        for v in self._vertices:
            H[(v,)] += B

        # encode H_A, ie each edge is adjacent to at least one colored vertex.
        for u, v in self._edges:
            H.add_constraint_OR(u, v, lam=A)

        return H.to_qubo()

    def convert_solution(self, solution):
        """convert_solution.

        Convert the solution to the QUBO or Ising to the solution to the Vertex
        Cover problem.

        Parameters
        ----------
        solution : iterable or dict.
            The QUBO or Ising solution output. The QUBO solution output
            is either a list or tuple where indices specify the label of the
            variable and the element specifies whether it's 0 or 1 for QUBO
            (or -1 or 1 for Ising), or it can be a dictionary that maps the
            label of the variable to is value.

        Return
        -------
        res : set.
            A set of which verticies need to be colored. Thus, if this
            function returns {0, 2}, then this means that vertex 0 and 2
            should be colored.

        """
        if not isinstance(solution, dict):
            solution = dict(enumerate(solution))
        return set(
            self._index_to_vertex[i] for i, x in solution.items() if x == 1
        )

    def is_solution_valid(self, solution):
        """is_solution_valid.

        Returns whether or not the proposed solution satisfies the constraint
        that every edge has at least one colored vertex.

        Parameters
        ----------
        solution : iterable or dict.
            solution can be the output of VertexCover.convert_solution,
            or the  QUBO or Ising solver output. The QUBO solution output
            is either a list or tuple where indices specify the label of the
            variable and the element specifies whether it's 0 or 1 for QUBO
            (or -1 or 1 for Ising), or it can be a dictionary that maps the
            label of the variable to is value.

        Return
        -------
        valid : boolean.
            True if the proposed solution is valid, else False.

        """
        if not isinstance(solution, set):
            solution = self.convert_solution(solution)

        return all(i in solution or j in solution for i, j in self._edges)
