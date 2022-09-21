# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:49:14 2020

@author: nicolas
"""
import xmltodict
from random import randint
        
class Prosecda_match():
    def __init__(self, xml_file):
        self.xml_annot = self._read_xml(xml_file=xml_file)
        self.inputs = Inputs(xml_inputs=self.xml_annot['inputs'])
        self.rule = Rule(xml_rule=self.xml_annot['family'])
        self.match_nb = int(self.xml_annot['proteins']['match_nb'])
        self.proteins = self._get_proteins(proteins=self.xml_annot['proteins']['protein'])
        
    def _read_xml(self, xml_file):
        with open(xml_file) as _f:
            xmldict = xmltodict.parse(_f.read())

        return xmldict['annotation']
    
    def _get_proteins(self, proteins):
        """ Returns a list of Protein instances """
        protein_list = []
        if isinstance(proteins, list):
            for protein in proteins:
                protein_list.append(Protein(protein=protein))
        else:
            protein_list.append(Protein(protein=proteins))
                
        return protein_list
        
    def get_protein_ids(self):
        return [ x.id for x in self.proteins ]
        
    def get_prot_by_id(self, _id=''):
        """
        Return Protein instance corresponding its the given id
        """
        return [ x for x in self.proteins if x.id == _id ][0]


class Inputs():
    def __init__(self, xml_inputs):
        self.domtblout = xml_inputs['domtblout']
        self.proteome = xml_inputs['proteome']
        self.yamlrules = xml_inputs['yamlrules']


class Rule:
    def __init__(self, xml_rule):
        self.name = xml_rule['name']
        self.comment = xml_rule['comment']
        self.mandatories = self._get_mandatories(mandatories=xml_rule['rule']['mandatories'])
        self.forbidden = self._get_forbidden(forbidden=xml_rule['rule']['forbidden'])

    def _get_mandatories(self, mandatories):
        if isinstance(mandatories['name'], list):
            return [ (name, score) for name, score in zip(mandatories['name'], mandatories['score']) ]
        else:
            return [(mandatories['name'], mandatories['score'])]
        
    def _get_forbidden(self, forbidden):
        if forbidden is None:
            return []
        else:
            return [forbidden['name']]

    def description(self):
        title = 'Description of the rule:\n'
        deco = '-' * len(title) + '\n'
        text = title + deco
        text += ' - name: {}\n'.format(self.name)
        text += ' - comment: {}\n'.format(self.comment)
        text += ' - mandatories:\n'.format()
        for mand, score in self.mandatories:
            text += '   - {} (score >= {})\n'.format(mand, score)
        text += ' - forbidden:\n'.format()
        if self.forbidden:
            for forbid in self.forbidden:
                text += '   - {}\n'.format(forbid)
        else:
            text += '   - None\n'
        text += deco
            
        return text


class Protein:
    def __init__(self, protein):
        self.id = protein['@id']
        self.sequence = protein['sequence']
        self.length = int(protein['length'])
        self.arch_nb = int(protein['architectures']['number'])
        self.architectures = self._get_architectures(architectures=protein['architectures']['architecture'])
        
    def _get_architectures(self, architectures):
        """ Returns a list of Architecture instances """
        arch_list = []
        if isinstance(architectures, list):
            for arch in architectures:
                instance = Architecture(architecture=arch)
                instance.sequence = self.sequence
                instance.length = self.length
                arch_list.append(instance) 
        else:
            instance = Architecture(architectures)
            instance.sequence = self.sequence
            instance.length = self.length
            arch_list.append(instance)

        return arch_list
        
    def get_matchingarch(self):
        return [ x for x in self.architectures if x.is_matching_rule ]
        
    def get_arch_ids(self):
        return [ x.id for x in self.architectures ]
        
    def get_arch_by_id(self, _id='1'):
        """
        Return Architecture instance corresponding its the given id
        """
        return [ x for x in self.architectures if x.id == _id ][0]
    

class Architecture:
    def __init__(self, architecture):
        self.id = architecture['@id']
        self.is_matching_rule = architecture['is_matching_rule']
        self.domain_nb = int(architecture['domains']['number'])
        self.domains = self._get_domains(domains=architecture['domains']['domain'])
        self.sequence = None
        self.length = None
        
    def _get_domains(self, domains): 
        """ Returns a list of Domain instances """
        domain_list = []
        if isinstance(domains, list):
            for domain in domains:
                domain_list.append(Domain(domain=domain)) 
        else:
            domain_list.append(Domain(domain=domains))
                
        return domain_list
        
    def get_domnames(self):
        return [ x.name for x in self.domains ]
        
    def colors_domain(self):
        colors = ['red', 'blue', 'yellow', 'pink', 'lightblue', 'orange', 'green']
        color_dict = {}
        for domain_name in set(self.get_domnames()):
            idx = randint(0, len(colors))
            color = colors[idx]
            colors.pop(idx)
            color_dict[domain_name] = color
            
        return color_dict
        
    def description(self):
        text = ''
        for domain in self.domains:
            text += '   - {}:'.format(domain.name)
            text += ' {}, {}, {}'.format(domain.from_, domain.to_, domain.score)
            text += '\n'
        
        return text
        
    def scale_domains(self, coef=1.0):
#        color_dict = self.colors_domain()
        scaled_domains = []
        for domain in self.domains:
            scaled_from = float(domain.from_)/float(self.length)*coef
            scaled_length = float(domain.length)/float(self.length)*coef   
            if len(domain.name) > 6:
                name = domain.name[0:3]+'...'
            else:
                name = domain.name
                
            scaled_dict = {'from': scaled_from, 'length': scaled_length,
                           'name': name}
            scaled_domains.append(scaled_dict)
            
        return scaled_domains


class Domain:
    def __init__(self, domain):
        self.name = domain['@name']
        self.sequence = domain['sequence']
        self.length = int(domain['length'])
        self.from_ = int(domain['from'])
        self.to_ = int(domain['to'])
        self.score = float(domain['score'])
        self.ival = float(domain['i-eval'])
        
        





if __name__ == '__main__':
    path2run = 'run_2020-04-28T13.28.38.475835/xml_matches/'
    path2xml = '/home/nicolas/spyder_workspace/ProSeCDA/prosecda/tests/prosecda_trial/'+path2run
    
    xml_file = path2xml+'Fusicocadiene_synthase.xml'
    xml_file = path2xml+'NRPS-like_b.xml'
    xml_file = path2xml+'Ent_kaurene_synthase.xml'
    
    match = Prosecda_match(xml_file=xml_file)
    match.get_protein_ids()
    match.match_nb
    match.xml_annot['family']['rule']['mandatories']['name']
    match.xml_annot['family']['rule']['mandatories']['score']
    type(match.xml_annot['family']['rule']['mandatories']['name'])
    
    rule = match.rule
    rule.name
    rule.comment
    rule.mandatories
    rule.forbidden
    print(rule.description())
    for mand, score in rule.mandatories:
        mand, score

        
    inputs = match.inputs
    inputs.domtblout
    inputs.proteome
    inputs.yamlrules
    
    proteins = match.proteins
    protein = proteins[0]
    protein.id
    protein.sequence
    protein.length
    protein.arch_nb
    protein.architectures
    architecture = protein.architectures[0]
        
    architecture.get_domnames()
    architecture.domains
    domain = architecture.domains[0]
    domain.from_
    domain.to_
    domain.score



#xmldict.keys()
#xmldict['annotation'].keys()
#
#xmldict['annotation']['inputs'].keys()
#xmldict['annotation']['inputs']['domtblout']
#xmldict['annotation']['inputs']['proteome']
#xmldict['annotation']['inputs']['yamlrules']
#
#xmldict['annotation']['family'].keys()
#xmldict['annotation']['family']['name']
#xmldict['annotation']['family']['comment']
#xmldict['annotation']['family']['rule']
#
#xmldict['annotation']['family']['rule'].keys()
#xmldict['annotation']['family']['rule']['mandatories'].keys()
#xmldict['annotation']['family']['rule']['mandatories']['name']
#xmldict['annotation']['family']['rule']['mandatories']['score']
#
#a=xmldict['annotation']['family']['rule']['forbidden'] #a is None if emty, a list otherwise
#    
#    
#xmldict['annotation']['proteins'].keys()
#xmldict['annotation']['proteins']['match_nb']
#protein = xmldict['annotation']['proteins']['protein'][0]
#protein.keys()
#protein['@id']
#protein['sequence']
#protein['length']
#protein['architectures'].keys()
#arch_nb = int(protein['architectures']['number'])
#if arch_nb > 1:
#    protein_arch = protein['architectures']['architecture'][0]
#else:
#    protein_arch = protein['architectures']['architecture']
#protein_arch.keys()
#protein_arch['@id']
#protein_arch['is_matching_rule']
#protein_arch['domains'].keys()
#domain_nb = int(protein_arch['domains']['number'])
#
#domains = protein_arch['domains']['domain']
#if isinstance(protein_arch['domains']['domain'], list):
#    for domain in domains:
#        domain['@name']
#        domain['sequence']
#        domain['length']
#        domain['from']
#        domain['to']
#        domain['score']
#        domain['i-eval']
#else:
#    domains['@name']
#    domains['sequence']
#    domains['length']
#    domains['from']
#    domains['to']
#    domains['score']
#    domains['i-eval']
#
#
#type(protein['architectures']['architecture'])
#type(protein['architectures']['architecture'][0])
