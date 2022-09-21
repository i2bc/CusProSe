import json
import logging
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import os


import prosecda.lib.rule_parser as rule_parser
from lib.external import Protein, DOMAIN_COLORS
import lib.logHandler as logHandler

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib.backends.backend_pdf').disabled = True

from ..lib import html


class Matches:
    """

    Container used to search and deal with all Match instances

    """
    def __init__(self, param):
        """

        @param param: instance of prosecda.lib.parameters
        """
        self.param = param
        self.list = []
        self.outdir = param.outdirname + 'results/'

        self.logger = logHandler.Logger(name=__name__)

    def add(self, match: None):
        """

        @param match: a Match instance
        @return: None
        """
        self.list.append(match)

    def search(self, rules: list, proteins: list):
        """
        Searches proteins matching defined rules.

        @param rules: list of Rules.Rule instances
        @param proteins: list of external.Protein instances
        @return: None
        """
        match = None
        for rule in rules:
            for protein in proteins:
                if is_match(rule, protein):
                    if not self.is_match_in_list(name=rule.name):
                        match = Match(rule=rule)
                        self.add(match=match)

                    match.add(protein=protein)

    def is_match_in_list(self, name: str):
        return name in self.get_rulenames()

    def get_rulenames(self) -> list:
        """

        Get all name of rules present in self.list

        @return: list
        """
        if self.list:
            return sorted([x.rule.name for x in self.list])
        else:
            return []

    def report(self):
        json_all_match = []
        if self.list:
            os.makedirs(self.outdir, exist_ok=True)
            for match in self.list:
                match.report(outdir=self.outdir, nopdf=self.param.nopdf)
                json_all_match.append(match.jsonify())

        html.generate_html(self.outdir)
        with open(self.outdir + '/data.json', 'w') as _jsonfile:
            _jsonfile.write(json.dumps(json_all_match, indent=4))


def is_match(rule, protein):
    protein_architecture = protein.best_architecture

    if True in [x in [y.name for y in rule.forbidden_domains] for x in protein_architecture.domain_names()]:
        return False
    elif sum([x.name in protein_architecture.domain_names() for x in rule.mandatory_domains]) < len(
            rule.mandatory_domains):
        return False
    else:
        mandatories_in_architecture = (x for x in protein_architecture.domains if
                                       x.qname in [y.name for y in rule.mandatory_domains])
        encountered_names = []

        for protein_domain in mandatories_in_architecture:
            for mandatory_domain in rule.mandatory_domains:
                if protein_domain.qname == mandatory_domain.name and mandatory_domain.name not in encountered_names:
                    if protein_domain.dom_ival <= mandatory_domain.ival:
                        encountered_names.append(mandatory_domain.name)

        if len(encountered_names) == len(rule.mandatory_domains):
            return True
        else:
            return False


class Match:
    """
    Object used to deal with all proteins matching a given rule.

    Attributes:
        - rule: instance of rule_parser.Rule
        - proteins: list containing all Protein instances matching the rule
        - domain_colors: variable used to store assigned colors to domains in proteins
    """

    palette = ['dodgerblue', 'orange', 'darkseagreen',
               'red', 'lightsalmon', 'steelblue',
               'cyan', 'teal', 'darkkhaki',
               'firebrick', 'greenyellow', 'mediumvioletred',
               'midnightblue', 'tan', 'rosybrown']

    def __init__(self, rule: rule_parser.Rule):
        """
        @param rule: instance of Rule
        """
        self.rule = rule
        self.proteins = []

        self.domain_colors = None

        self.logger = logHandler.Logger(name=__name__)

    def add(self, protein=None):
        if protein not in self.proteins:
            self.proteins.append(protein)

    def set_colors(self):
        domains_set = self.list_domains()
        if len(domains_set) <= len(self.palette):
            self.domain_colors = {x: self.palette[i] for i, x in enumerate(self.list_domains())}

    def list_domains(self) -> list:
        """

        Get a non-redundant list of all domain names of proteins in self.proteins

        @return: list
        """
        all_lists = [x.list_domains() for x in self.proteins]

        if all_lists:
            return sorted(set([item for sublist in all_lists for item in sublist]))
        else:
            return []

    def report(self, outdir: str, nopdf: bool):
        self.set_colors()

        outpath = outdir + self.rule.name + '/'
        os.makedirs(outpath, exist_ok=True)

        self.logger.title('Proteins matching {} rule:'.format(self.rule.name))

        if not nopdf:
            pdf_pages = PdfPages(filename=outpath + 'all_' + self.rule.name + '.pdf')

        for protein in self.proteins:
            self.logger.info(' - {}'.format(protein.name))

            protein.write_fasta(outdir=outpath)
            protein.write_xml(outdir=outpath, rule=self.rule)

            if not nopdf:
                self.plot_protein_best_architecture(protein=protein, pdf_pages=pdf_pages)
                self.plot_protein_all_domains(protein=protein, outpath=outpath)

        if not nopdf:
            pdf_pages.close()

    def plot_protein_best_architecture(self, protein: Protein, pdf_pages: PdfPages):
        protein_best_architecture = PlotProt(protein=protein, colors=self.domain_colors)
        protein_best_architecture.draw()
        protein_best_architecture.save(pdf_pages=pdf_pages)

    def plot_protein_all_domains(self, protein: Protein, outpath: str):
        protein_all_domains = PlotProt(protein=protein, colors=self.domain_colors, _type='all')
        protein_all_domains.draw()
        protein_all_domains.save(outpath=outpath)

    def jsonify(self):
        proteins = [protein.jsonify() for protein in self.proteins]
        json_rule = self.rule.jsonify()

        for mandatory in json_rule["mandatories"]:
            mandatory["color"] = DOMAIN_COLORS[mandatory["name"]]

        for forbidden in json_rule["forbidden"]:
            forbidden["color"] = DOMAIN_COLORS[forbidden["name"]]

        json_match = {
            "name": self.rule.name,
            "rules": json_rule,
            "proteins": proteins
            }

        return json_match


class PlotProt:
    def __init__(self, protein, colors=None, _type='architecture'):
        self.protein = protein
        self.colors = colors
        self.type = _type

        if self.type == 'architecture':
            self.domains = protein.best_architecture.domains
            self.start_domain_plot = 1
        elif self.type == 'all':
            self.domains = protein.domains
            self.start_domain_plot = 0

        self.domains_nb = len(self.domains)
        self.delta = self.protein.length * 0.01
        self.n_max_rows = 20 + 1
        self.gs = gridspec.GridSpec(nrows=self.n_max_rows, ncols=6)

        self.plots = self.create_fig()

    def create_fig(self):
        n_figs = self.domains_nb // (self.n_max_rows - 1) + (self.domains_nb % (self.n_max_rows - 1) > 0)
        plots = {}
        for i in range(n_figs):
            figure = plt.figure(figsize=(8, 10))
            figure.subplots_adjust(left=0.075, bottom=0.1, right=0.925, top=0.9, wspace=0.105, hspace=0.2)

            axs_draw = [figure.add_subplot(self.gs[x, :-3]) for x in range(self.n_max_rows)]
            [x.set_axis_off() for x in axs_draw]

            axs_text = [figure.add_subplot(self.gs[x, -3:]) for x in range(self.n_max_rows)]
            [x.set_axis_off() for x in axs_text]
            start = i * (self.n_max_rows - 1)
            end = start + self.n_max_rows - 1

            if n_figs == 1:
                title = self.protein.name
            else:  # n_figs > 1
                title = self.protein.name + '_part-' + str(n_figs + 1)

            plots[i] = {'fig': figure,
                        'axs_draw': axs_draw,
                        'axs_text': axs_text,
                        'domains_idx': (start, end),
                        'title': title
                        }

        return plots

    def draw(self):
        for i in self.plots:
            if self.type == 'architecture':
                self.draw_protein(ax=self.plots[i]['axs_draw'][0])

            start = self.plots[i]['domains_idx'][0]
            end = self.plots[i]['domains_idx'][1]
            for j, domain in enumerate(self.domains[start:end], start=self.start_domain_plot):
                self.draw_sequence(ax=self.plots[i]['axs_draw'][j])
                self.draw_domain(domain=domain, ax=self.plots[i]['axs_draw'][j])

                pos_from = domain.env_from - self.delta  # - len(str(domain.env_from))
                pos_to = domain.env_to + self.delta  # + len(str(domain.env_to))
                self.plots[i]['axs_draw'][j].text(pos_from, 7, str(domain.env_from), fontsize=7, ha='right')
                self.plots[i]['axs_draw'][j].text(pos_to, 7, str(domain.env_to), fontsize=7)

                # plots text to annote the domains
                domain_name = r'$\bf{' + domain.qname.replace('_', '\_') + ':' + '}$'
                text = ' i-evalue = {}, score = {}'.format(domain.dom_ival, domain.dom_score)
                self.plots[i]['axs_text'][j].text(0.055, 0.35, domain_name + text, fontsize=9)

                suptitle = self.plots[i]['title']
                self.plots[i]['fig'].suptitle(suptitle, fontsize=12, fontweight='bold')

    def draw_protein(self, ax):
        self.draw_sequence(ax=ax)
        for domain in self.domains:
            self.draw_domain(domain=domain, ax=ax)

        ax.text(1 - self.delta, 9, '1', fontsize=8, ha='right')
        ax.text(self.protein.length, 9, str(self.protein.length), fontsize=8)

    def draw_sequence(self, ax):
        ax.set_xlim([1, self.protein.length])
        ax.set_ylim([0, 10])

        mean_ax_lim = (ax.get_ylim()[1] - ax.get_ylim()[0]) / 2.
        width = self.protein.length
        height = 0.2
        x = 1
        y = mean_ax_lim - height / 2.

        ax.add_patch(
            patches.Rectangle(
                (x, y),
                width,
                height,
                color='darkslategrey',
                alpha=0.95
            )
        )

    def draw_domain(self, domain, ax):
        """
        Draws a domain
        """
        if not self.colors:
            color = 'orange'  # 'dodgerblue'
        else:
            color = self.colors[domain.qname]
        start_pos = domain.env_from
        end_pos = domain.env_to

        mean_ax_lim = (ax.get_ylim()[1] - ax.get_ylim()[0]) / 2
        width = (end_pos - start_pos)
        height = mean_ax_lim * 1
        x = start_pos
        y = mean_ax_lim - height / 2.

        ax.add_patch(
            patches.Rectangle(
                (x, y),
                width,
                height,
                facecolor=color,
                edgecolor='black',
                alpha=0.75,
                label=domain.qname
            )
        )

    def save(self, pdf_pages=None, outpath=None):
        if pdf_pages:
            for i in self.plots:
                pdf_pages.savefig(self.plots[i]['fig'])
                plt.close(self.plots[i]['fig'])
        elif outpath:
            for i in self.plots:
                self.plots[i]['fig'].savefig(outpath + self.plots[i]['title'] + '.pdf')
                plt.close(self.plots[i]['fig'])
