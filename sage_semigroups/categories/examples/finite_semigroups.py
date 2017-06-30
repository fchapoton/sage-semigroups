"""
    sage: import sage_semigroups # random
"""
from sage.categories.semigroups import Semigroups
from sage.structure.parent import Parent

class LeftRegularBand:

    # READY
    def __init__(self, alphabet=('a','b','c','d'), category=None):
        r"""
        A left regular band.

        EXAMPLES::

            sage: S = FiniteSemigroups().example(); S
            An example of a finite semigroup: the left regular band generated by ('a', 'b', 'c', 'd')
            sage: S = FiniteSemigroups().example(alphabet=('x','y')); S
            An example of a finite semigroup: the left regular band generated by ('x', 'y')
            sage: TestSuite(S).run()

            sage: S = FiniteSemigroups().example(category=Semigroups().RTrivial())
            sage: S.category()
            sage: TestSuite(S).run()
        """
        self.alphabet = alphabet
        category = Semigroups().Finite().FinitelyGenerated().or_subcategory(category)
        Parent.__init__(self, category=category)


