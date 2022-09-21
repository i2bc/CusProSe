import lib.logHandler as logHandler
from lib.external import HmmerDomtbl, Architecture, Protein
import networkx as nx
# import matplotlib.pyplot as plt


class Path:
    """

    Container used to search possible domain architectures.

    """
    def __init__(self, protein: Protein):
        """

        @param protein: instance of Protein
        """
        self.protein = protein
        self.edges = []

        self.logger = logHandler.Logger(name=__name__)

    def add_virtual_domains(self):
        """

        Creates and adds virtual HmmerDomtbl instance at each extremity of the
        of the protein domain list in order to make process of searching path
        easier with only one start point and one end point.
        The final step sorts all domains of the Hmm_query instance by their
        position in ascending order.

        """
        cols = []
        hmmer_type = 'search'
        virtual_start = HmmerDomtbl(cols=cols, hmmer_type=hmmer_type)
        virtual_end = HmmerDomtbl(cols=cols, hmmer_type=hmmer_type)
        virtual_start.qname, virtual_end.qname = 'virtual_start', 'virtual_end'
        virtual_start.dom_id, virtual_end.dom_id = 1, 1
        virtual_start.env_from, virtual_start.env_to = -10, -5

        max_coor = max([dom.env_to for dom in self.protein.domains])
        virtual_end.env_from, virtual_end.env_to = max_coor + 5, max_coor + 10

        self.protein.domains = [x[0] for x in sorted([(x, x.env_from) for x in self.protein.domains], key=lambda x: x[1])]
        self.protein.domains.insert(0, virtual_start)
        self.protein.domains.append(virtual_end)

    def get_edges(self) -> list:
        """

        Finds all non-overlapping contiguous domain pairs (edges).

        Returns: list of tuple of HmmerDomTbl instances
        """
        for i, dom_i in enumerate(self.protein.domains):
            for j, dom_j in enumerate(self.protein.domains):
                if j > i:
                    if self.is_edge(domain_i=dom_i, domain_j=dom_j):
                        self.edges.append((dom_i, dom_j))

    def is_edge(self, domain_i: HmmerDomtbl, domain_j: HmmerDomtbl) -> bool:
        flag = False
        if not self.is_overlap(domain_i.env_coors(), domain_j.env_coors()):
            if self.are_contiguous(domain_i=domain_i, domain_j=domain_j):
                flag = True

        return flag

    @staticmethod
    def is_overlap(coors_i: (list or tuple), coors_j: (list or tuple), ovp_co=0.4) -> bool:
        """

        Function defining if the given coordinates of two elements are overlapping.
        Two elements are considered to be overlapping is, by default, at least 40 %
        of the shortest element sequence overlap with the other element.

        Let's consider two elements i and j such as:

        coors_i = (X1, Y1)
        coors_j = (X2, Y2)

         ------X1**************Y1-------------
         -----------------X2******Y2-----

        The procedure is as follow:
         1 - find the shortest element: j
         2 - find the maximum X coordinate: X2
         3 - find the minimum Y coordinate: Y1
         4 - if len(Y1 - X2) <= len(j) * ovp_co:
                then elements are considered as non-overlapping
             else:
                elements are considered as overlapping

        @param coors_i: list or tuple of coordinates for element i
        @param coors_j: list or tuple of coordinates for element j
        @param ovp_co: allowed percentage threshold of the shortest sequence element used to define it as non-overlapping
        @return: True if overlap, False otherwise
        """
        sequence_length_i = (coors_i[1] - coors_i[0] + 1)
        sequence_length_j = (coors_j[1] - coors_j[0] + 1)
        sequence_length_shortest = min(sequence_length_i, sequence_length_j)

        x_max = max(coors_i[0], coors_j[0])
        y_min = min(coors_i[1], coors_j[1])

        return y_min - x_max + 1 > ovp_co * sequence_length_shortest

    def are_contiguous(self, domain_i: HmmerDomtbl, domain_j: HmmerDomtbl) -> bool:
        """

        Checks if no domain is present between domain_i and domain_j.

        Case where domains i and j are contiguous (no domain between them):

        --x_domain_i_y-------------------------------------------------
        -----------------------------x_domain_j_y----------------------
        -------------------------------------------------x_domain_y----

        Cases where domains i and j are not contiguous:

        --x_domain_i_y-------------------------------------------------
        -----------------------------x_domain_j_y----------------------
        -----------------x_domain_y------------------------------------

        --x_domain_i_y-------------------------------------------------
        -----------------x_domain_j_y----------------------------------
        ----------x_domain_y-------------------------------------------


        @param domain_i: domain on the left of domain_j
        @param domain_j: domain on the right of domain_i
        @return: True if a domain is present, False otherwise
        """
        y_domain_i = domain_i.env_to
        x_domain_j = domain_j.env_from

        is_contiguous = True
        for domain in self.protein.domains:
            if domain.env_to < x_domain_j and domain.env_from > y_domain_i:
                is_contiguous = False
                break

        return is_contiguous

    def search(self):
        """

        Finds all possible combinations/architectures of non-overlapping domains.

        """
        self.logger.debug(' - starting path search for {}...'.format(self.protein.name))

        self.add_virtual_domains()
        self.get_edges()

        graph = nx.DiGraph()
        graph.add_edges_from(self.edges)

        # H = nx.relabel_nodes(graph, {x: x.qname + '-' + str(x.dom_id) for x in list(graph.nodes)})
        #
        # f = plt.figure()
        # nx.draw(H, ax=f.add_subplot(111), with_labels=True)
        # f.savefig(self.protein.name + '.png')

        source = self.protein.domains[0]  # 'virtual_start' domain
        target = self.protein.domains[-1]  # 'virtual_end' domain

        paths = (path for path in nx.all_simple_paths(graph, source=source, target=target))
        paths = sorted([x for x in paths], key=lambda x: len(x))
        self.logger.debug('  - {} total path found'.format(len(paths)))

        self.rm_virtual_domains()
        longest_paths = self.get_longest_paths(paths=paths)

        for i, path in enumerate(longest_paths, start=1):
            domains = [x for x in path if x.qname not in ['virtual_start', 'virtual_end']]
            self.protein.architectures.append(Architecture(_id=str(i), domains=domains))

    def rm_virtual_domains(self):
        """

        Removes virtual domains.

        @return: None
        """
        [self.protein.domains.remove(x) for x in self.protein.domains if x.qname in ['virtual_start', 'virtual_end']]

    def get_longest_paths(self, paths):
        return [x for x in paths if x not in self.get_subpaths(paths=paths)]

    @staticmethod
    def get_subpaths(paths):
        subpaths = []
        for i, path_i in enumerate(paths):
            for j, path_j in enumerate(paths):
                if j > i:
                    if sum([x in path_j for x in path_i]) == len(path_i):
                        if path_i not in subpaths:
                            subpaths.append(path_i)

        return subpaths
