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

"""_qubo.py.

Contains the QUBO class. See ``help(qubovert.QUBO)``.

"""

from .utils import BO, QUBOMatrix


__all__ = 'QUBO',


class QUBO(BO, QUBOMatrix):
    """QUBO.

    Class to manage converting general QUBO problems to and from their
    QUBO and Ising formluations.

    This class deals with QUBOs that have binary labels that do not range from
    0 to n-1. If your labels are nonnegative integers, consider using
    ``qubovert.utils.QUBOMatrix``. Note that it is generally
    more efficient to initialize an empty QUBO object and then build the
    QUBO, rather than initialize a QUBO object with an already built dict.

    QUBO inherits some methods and attributes the ``QUBOMatrix`` class. See
    ``help(qubovert.utils.QUBOMatrix)``.

    QUBO inherits some methods and attributes the ``BO`` class. See
    ``help(qubovert.utils.BO)``.

    Example usage
    -------------
    >>> qubo = QUBO()
    >>> qubo[('a',)] += 5
    >>> qubo[(0, 'a')] -= 2
    >>> qubo -= 1.5
    >>> qubo
    {('a',): 5, ('a', 0): -2, (): -1.5}

    >>> qubo = QUBO({('a',): 5, (0, 'a'): -2, (): -1.5})
    >>> qubo
    {('a',): 5, ('a', 0): -2, (): -1.5}
    >>> Q = qubo.to_qubo()
    >>> Q
    {(0,): 5, (0, 1): -2, (): -1.5}
    >>> qubo.convert_solution({0: 1, 1: 0})
    {'a': 1, 0: 0}

    Note 1
    ------
    Note that keys will end up sorted by their hash. Hashes will not be
    consistent across Python sessions (unless they are integers)! For example,
    both of the following can happen:

    >>> print(QUBO({('a', 0): 1, (0, 1): -1}))
    {('a', 0): 1, (0, 1): -1}

    or

    >>> print(QUBO({('a', 0): 1, (0, 1): -1}))
    {(0, 'a'): 1, (0, 1): -1}

    But the following will never happen:

    >>> print(QUBO({('a', 0): 1, (0, 1): -1}))
    {('a', 0): 1, (1, 0): -1}

    Ie integers will always be correctly sorted.

    Note 2
    ------
    For efficiency, many internal variables including mappings are computed as
    the problemis being built. This can cause these
    values to be wrong for some specific situations. Calling ``refresh``
    will rebuild the dictionary, resetting all of the values. See
    ``help(QUBO.refresh)``

    Examples
    --------
    >>> from qubovert import QUBO
    >>> Q = HIsing()
    >>> Q[('a',)] += 1
    >>> Q, Q.mapping, Q.reverse_mapping
    {('a',): 1}, {'a': 0}, {0: 'a'}
    >>> Q[('a',)] -= 1
    >>> Q, Q.mapping, Q.reverse_mapping
    {}, {'a': 0}, {0: 'a'}
    >>> Q.refresh()
    >>> Q, Q.mapping, Q.reverse_mapping
    {}, {}, {}

    """

    def __init__(self, *args, **kwargs):
        """__init__.

        This class deals with QUBOs that have binary labels that do not range
        from 0 to n-1. If your labels are nonnegative integers, consider using
        ``qubovert.utils.QUBOMatrix``. Note that it is generally more efficient
        to initialize an empty QUBO object and then build the QUBO, rather than
        initialize a QUBO object with an already built dict.

        Parameters
        ----------
        args and kwargs : define a dictionary with ``dict(*args, **kwargs)``.
            The dictionary will be initialized to follow all the convensions of
            the class.

        Examples
        -------
        >>> qubo = QUBO()
        >>> qubo[('a',)] += 5
        >>> qubo[(0, 'a')] -= 2
        >>> qubo -= 1.5
        >>> qubo
        {('a',): 5, ('a', 0): -2, (): -1.5}

        >>> qubo = QUBO({('a',): 5, (0, 'a'): -2, (): -1.5})
        >>> qubo
        {('a',): 5, ('a', 0): -2, (): -1.5}

        """
        BO.__init__(self, *args, **kwargs)
        QUBOMatrix.__init__(self, *args, **kwargs)

    def to_qubo(self):
        """to_qubo.

        Create and return upper triangular QUBO representing the problem.
        The labels will be integers from 0 to n-1.

        Return
        -------
        Q : qubovert.utils.QUBOMatrix object.
            The upper triangular QUBO matrix, a QUBOMatrix object.
            For most practical purposes, you can use QUBOMatrix in the
            same way as an ordinary dictionary. For more information,
            see ``help(qubovert.utils.QUBOMatrix)``.

        """
        Q = QUBOMatrix()

        for k, v in self.items():
            key = tuple(self._mapping[i] for i in k)
            Q[key] += v

        return Q

    def convert_solution(self, solution):
        """convert_solution.

        Convert the solution to the integer labeled QUBO to the solution to
        the originally labeled QUBO.

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
        res : dict.
            Maps binary variable labels to their QUBO solutions values {0, 1}.

        Example
        -------
        >>> qubo = QUBO({('a',): 1, ('a', 'b'): -2, ('c',): 1})
        >>> Q = qubo.to_qubo()
        >>> Q
        {(0,): 1, (0, 1): -2, (2,): 1}
        >>> solution = solve_qubo(Q)  # any solver you want
        >>> solution
        [1, 1, 0]  # or {0: 1, 1: 1, 2: 0}
        >>> sol = qubo.convert_solution(solution)
        >>> sol
        {'a': 1, 'b': 1, 'c': 0}

        >>> qubo = QUBO({('a',): 1, ('a', 'b'): -2, ('c',): 1})
        >>> L = qubo.to_ising()
        >>> solution = solve_ising(L)  # any solver you want
        >>> solution
        [1, 1, -1]  # or {0: 1, 1: 1, 2: -1}
        >>> sol = qubo.convert_solution(solution)
        >>> sol
        {'a': 1, 'b': 1, 'c': 0}

        """
        return {
            self._reverse_mapping[i]: 1 if solution[i] == 1 else 0
            for i in range(self.num_binary_variables)
        }

    @staticmethod
    def _check_key_valid(key):
        """_check_key_valid.

        Internal method to check if an input key to the dictionary is valid.
        Checks to see if ``key`` is a tuple.

        Parameters
        ---------
        key : anything, but must be a tuple to be valid.

        Returns
        -------
        None.

        Raises
        ------
        KeyError if the key is invalid.

        """
        # override QUBOMatrix._check_key_valid to allow for noninteger keys.
        if not isinstance(key, tuple) or len(set(key)) > 2:
            raise KeyError(
                "Key formatted incorrectly, must be tuple of <= 2 unique "
                "elements")
