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

"""_problem_parentclass.py.

This file contains the class Problem, which is the parent class to all
the problem classes.

"""

from . import qubo_to_ising, ising_to_qubo, solve_qubo_bruteforce


class Problem:
    """Problem.

    This acts a parent class to all the QUBO and Ising conversion problem
    classes. The ``__new__`` method keeps track of the problem args. The
    ``repr`` method uses those input args, such that
    ``eval(repr(cls)) == cls``. Finally, we define a ``__eq__`` method to
    determine if two problems are the same. The rest of the methods are to be
    implemented in child classes.

    Additionally, his class defines the ``to_qubo`` and ``to_ising`` methods.
    ``to_qubo`` calls ``to_ising`` and then converts from ising to qubo.
    ``to_ising`` calls ``to_qubo`` and then converts from qubo to ising. Thus,
    the child classes MUST define either ``to_qubo`` or ``to_ising``. In this
    way, by only defining one of those, both are implemented.
    """

    def __new__(cls, *args, **kwargs):
        """__new__.

        Creates the object and keeps track of the input arguments and keyword
        arguments. Child classes should not change this. This method will be
        called before every __init__ is called. We use __new__ to keep track
        of input arguments instead of using __init__ so that child class
        implementations don't have to worry about it. Ie child classes
        don't have to call `super().__init__(*args, **kwargs)` in their
        __init__ method.

        Parameters
        ---------
        Defined in child classes.

        Return
        -------
        obj : instance of the child class.

        """
        # obj = object.__new__(cls)
        obj = super().__new__(cls)
        obj._problem_args, obj._problem_kwargs = args, kwargs.copy()
        return obj

    @property
    def num_binary_variables(self):
        """num_binary_variables.

        The number of binary variables that the QUBO/Ising uses. Should be
        implemented in the child class.

        Return
        -------
        num : int.
            The number of variables in the QUBO/Ising formulation.

        """
        raise NotImplementedError("Method to be implemented in child classes")

    def __repr__(self):
        """__repr__.

        Same as __str__, but will give a truncted output.

        Return
        -------
        s : str.

        """
        s = str(self)
        if len(s) < 37:
            return s
        return s[:37] + " ..."

    def __str__(self):
        """__str__.

        Defined such that the following is true (assuming you have imported
        * from qubovert.problems).

        >>> s = Class_derived_from_Problem(*args)
        >>> eval(str(s)) == s
        True

        Return
        -------
        s : str.

        """
        s = self.__class__.__name__ + "("
        if not self._problem_args and not self._problem_kwargs:
            return s + ")"
        for a in self._problem_args:
            val = str(a) if not isinstance(a, str) else "'%s'" % a
            s += val + ", "
        for k, v in self._problem_kwargs.items():
            val = str(v) if not isinstance(v, str) else "'%s'" % v
            s += str(k) + "=" + val + ", "
        return s[:-2] + ")"

    def __eq__(self, other):
        """__eq__.

        Determine if ``self`` and ``other`` define the same problem.

        Parameters
        ----------
        other : an object derived from the ``Problem`` class.

        Return
        -------
        eq : boolean.
            If ``self`` and ``other`` represent the same problem.

        """
        return (
            isinstance(other, type(self)) and
            self._problem_args == other._problem_args and
            self._problem_kwargs == other._problem_kwargs
        )

    def to_qubo(self, *args, **kwargs):
        """to_qubo.

        Create and return upper triangular QUBO representing the problem.
        Should be implemented in child classes. If this method is not
        implemented in the child class, then it simply calls to_ising and
        converts the ising formulation to a QUBO formulation.

        Parameters
        ----------
        Defined in the child class. They should be parameters that define
        lagrange multipliers or factors in the QUBO.

        Return
        -------
        result : tuple (Q, offset).
            Q : qubovert.utils.QUBOMatrix object.
                The upper triangular QUBO matrix, a QUBOMatrix object.
                For most practical purposes, you can use QUBOMatrix in the
                same way as an ordinary dictionary. For more information,
                see ``help(qubovert.utils.QUBOMatrix)``.
            offset : float.
                The sum of the terms in the formulation that don't involve any
                variables.

        """
        return ising_to_qubo(*self.to_ising(*args, **kwargs))

    def to_ising(self, *args, **kwargs):
        """to_ising.

        Create and return upper triangular J representing the coupling of the
        Ising formulation of the problem and the h representing the field.
        Should be implemented in child classes. If this method is not
        implemented in the child class, then it simply calls to_qubo and
        converts the QUBO formulation to an Ising formulation.

        Parameters
        ----------
        Defined in the child class. They should be parameters that define
        lagrange multipliers or factors in the Ising model.

        Return
        ------
        result : tuple (h, J, offset).
            h : qubovert.utils.IsingField object.
                The field of each spin in the Ising formulation.
                h is a IsingField object. For most practical purposes, you can
                use IsingField in he same way as an ordinary dictionary. For
                more information, see ``help(qubovert.utils.IsingField)``.
            J : qubovert.utils.IsingCoupling object.
                The upper triangular coupling matrix, an IsingCoupling object.
                For most practical purposes, you can use IsingCoupling in the
                same way as an ordinary dictionary. For more information,
                see ``help(qubovert.utils.IsingCoupling)``.
            offset : float.
                It is the sum of the terms in the formulation that don't
                involve any variables.

        """
        return qubo_to_ising(*self.to_qubo(*args, **kwargs))

    def convert_solution(self, solution, *args, **kwargs):
        """convert_solution.

        Convert the solution to the QUBO to the solution to the problem.
        Should be implemented in child classes. If it is not implemented in the
        child class, then this function will by default return the same
        solution as what inputted.

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
        Implemented in the child class.

        """
        return solution

    def is_solution_valid(self, solution, *args, **kwargs):
        """is_solution_valid.

        Returns whether or not the proposed solution is valid. Should be
        implemented in child classes. If it is not implemented in the child
        class, then this function will by default return True.

        Parameters
        ----------
        solution : iterable or dict.
            solution can be the output of ``convert_solution``,
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
        return True

    def solve_bruteforce(self, *args, **kwargs):
        """solve_bruteforce.

        Solve the problem bruteforce. THIS SHOULD NOT BE USED FOR LARGE
        PROBLEMS! This is implemented in the parent ``qubovert.utils.Problem``
        class. Some problems use a lot of slack binary variables for their
        QUBO/Ising formulations. If this is the case, then the child class
        for this problem should override this method with a better bruteforce
        solver. But, for problems that do not use slack variables, this
        method will suffice. It converts the problem to QUBO, solves it with
        ``qubovert.utils.solve_qubo_bruteforce``, and then calls and returns
        ``convert_solution``.

        Parameters
        ----------
        *args and **kwargs : arguments and keyword arguments.
            Contains args and kwargs for the ``to_qubo`` method. Also contains
            a ``all_solutions`` boolean flag, which indicates whether or not
            to return all the solutions, or just the best one found.
            ``all_solutions`` defaults to False.

        Return
        ------
        res : the output or outputs of the ``convert_solution`` method.
            If ``all_solutions`` is False, then ``res`` is just the output
            of the ``convert_solution`` method.
            If ``all_solutions`` is True, then ``res`` is a list of outputs
            of the ``convert_solution`` method, e.g. a converted solution
            for each solution that the bruteforce solver returns.

        """
        kwargs = kwargs.copy()
        all_solutions = kwargs.pop("all_solutions", False)
        qubo = self.to_qubo(*args, **kwargs)
        _, sol = solve_qubo_bruteforce(*qubo, all_solutions=all_solutions)
        if all_solutions:
            return [self.convert_solution(x) for x in sol]
        return self.convert_solution(sol)
