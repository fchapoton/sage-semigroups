r"""
Karnofsky-Rhodes expansion of a monoid

EXAMPLES::

    sage: import sage_semigroups
    Loading sage-semigroups and patching its features into Sage's library: ...
"""
from sage.combinat.words.finite_word import FiniteWord_class
from sage.combinat.words.words import Words
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.structure.element_wrapper import ElementWrapper
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.sets.family import Family
from sage.categories.monoids import Monoids
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.sets.set import Set

class KarnofskyRhodesExpansion(UniqueRepresentation, Parent):
    def __init__(self, monoid, generators=None):
        r"""
        EXAMPLES::

            sage: from sage_semigroups.monoids.karnofsky_rhodes_expansion import KarnofskyRhodesExpansion
            sage: from sage_semigroups.monoids.free_left_regular_band import FreeLeftRegularBand
            sage: F = FreeLeftRegularBand(2); F
            Free left regular band generated by ('a', 'b')
            sage: K = KarnofskyRhodesExpansion(F); K
            Karnofsky-Rhodes expansion of Free left regular band generated by ('a', 'b')
            sage: TestSuite(K).run()

        """
        self._underlying_monoid = monoid
        if generators is None:
            generators = monoid.semigroup_generators()
        self._words = Words(generators)
        self._underlying_monoid_generators = Family(generators)
        Parent.__init__(self, category=Monoids().Finite().FinitelyGenerated())
        self._representatives = {self._canonicalize(self.one()): self.one()}

        # TODO: do we really want to do this?!
        # force the generation of all the elements
        self.list()

    def succ_generators(self, side="twosided"):
        def fcn(x):
            pgens = []
            if side == "right"  or side == "twosided":
                pgens += [self(x.value * g.value) for g in self.semigroup_generators()]
            if side == "left" or side == "twosided":
                pgens += [self(g.value * x.value) for g in self.semigroup_generators()]
            gens = []
            for gen in pgens:
                mT = self._canonicalize(gen)
                if mT not in self._representatives:
                    gens.append(gen)
                    self._representatives[mT] = gen
                elif self._representatives[mT] == gen:
                    gens.append(gen)
            return gens
        return fcn

    def _repr_(self):
        return "Karnofsky-Rhodes expansion of %s"%(self._underlying_monoid,)

    @cached_method
    def one(self):
        return self(self._words())

    def _canonicalize(self,x):
        m = self.projection(x)
        T = self.path_transition_edges(x)
        return (m,T)

    def representative(self, x):
        return self._representatives[self._canonicalize(x)]

    def product(self, x, y):
        return self.representative(self(x.value * y.value))
        return self.representative(self.representative(x).value * self.representative(y).value)

    def semigroup_generators(self):
        return Family([self(self._words((i,))) for i in self._underlying_monoid_generators])

    def an_element(self):
        return self.one()

    @lazy_attribute
    def _underlying_monoid_cayley_graph(self):
        return self._underlying_monoid.cayley_graph(side="right",
                generators=self._underlying_monoid_generators)

    @lazy_attribute
    def _transition_edges(self):
        G = self._underlying_monoid_cayley_graph
        d = {}
        for (i,C) in enumerate(G.strongly_connected_components()):
            for v in C:
                d[v] = i
        transition_edges = Set([(a,b,l) for (a,b,l) in G.edges() if d[a] != d[b]])
        return transition_edges

    def projection(self, w):
        return self._underlying_monoid.prod(w.value)

    @lazy_attribute
    def _transition_dictionary(self):
        t = {}
        for (u,v,l) in self._underlying_monoid_cayley_graph.edge_iterator():
            t[u, l] = v
        return t

    def _read_path(self, w):
        t = self._transition_dictionary
        i = self._underlying_monoid_generators.inverse_family()
        v = self._underlying_monoid.one()
        path = []
        for a in w.value:
            w = t[v,i[a]]
            path.append((v,w,i[a]))
            v = w
        return path

    def path_transition_edges(self, w):
        tedges = self._transition_edges
        output = []
        for (a,b,l) in self._read_path(w):
            if (a,b,l) in tedges:
                output.append((a,b,l))
        return Set(output)

    def are_equivalent(self, u, v):
        assert u in self
        assert v in self
        return self.projection(u) == self.projection(v) and \
                    self.path_transition_edges(u) == self.path_transition_edges(v)

    def __iter__(self):
        from sage.combinat.backtrack import TransitiveIdeal
        return TransitiveIdeal(self.succ_generators(side = "right"), [self.one()]).__iter__()

    class Element (ElementWrapper):
        wrapped_class = FiniteWord_class
        __lt__ = ElementWrapper._lt_by_value

        def _eq_(self, other):
            return self.parent().are_equivalent(self, other)
