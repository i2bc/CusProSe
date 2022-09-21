# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:41:40 2020

@author: nicolas
"""
import yaml
import lib.logHandler as logHandler


class Parser:
    def __init__(self, input_filename: str, co_ival=None):
        self.input_filename = input_filename
        self.co_ival = co_ival
        self.rules = parse_yaml(input_filename=input_filename, co_ival=co_ival)

        self.logger = logHandler.Logger(name=__name__)

    def description(self):
        self.logger.title('Description of the rules')

        for rule in self.rules:
            rule.description()

    def list_alldomains(self) -> list:
        """

        @return: A non-redundant list of all domain names in all rules
        """
        mx_format = [x.list_domains() for x in self.rules]

        return sorted(set([val for sublist in mx_format for val in sublist]))


def parse_yaml(input_filename: str, co_ival=None):
    """
    Parses yaml file rules. Reading of yaml file returns a dictionary.
    The dictionary looks like: 
    {'PKS-NRPS-like_a': {'COMMENT': 'Hybrides PKS-NRPS like',
                     'CONDITION': {'mandatory': ['KS', 'C,10', 'AT,5'],
                                   'forbidden': ['PP-binding']}}
    Arguments:
        - filename: yaml rules filename
        - param: instance of parameters
    
    Return:
        - list of Rule instances
    """
    with open(input_filename, 'r') as input_file:
        yaml_data = yaml.load(input_file, Loader=yaml.FullLoader)
    rules = []
    for name in sorted(yaml_data):
        rules.append(Rule(name=name, rule_def=yaml_data[name], co_ival=co_ival))
        
    return rules
    

class Rule:
    """
    Wrapper containing all rules defining a given family
    
    Arguments:
        - name: family name (str)
        - rules: dictionary from yaml input
                 The dictionary looks like: 
                 {'PKS-NRPS-like_a': {'COMMENT': 'Hybrides PKS-NRPS like',
                                      'CONDITION': {'mandatory': ['KS', 'C,10', 'AT,5'],
                                                    'forbidden': ['PP-binding']}}
        - param: instance of Parameters
    """
    def __init__(self, name: str, rule_def: dict, co_ival=None):
        """

        @param name: name of the rule (i.e. the protein "family" name)
        @param rule_def: dictionary containing criteria to define the rule
        @param co_ival: cutoff threshold of hmmer i-evalue
        """
        self.name = name
        self.rule_def = rule_def
        self.comment = rule_def['COMMENT']
        self.co_ival = co_ival

        self.mandatory_domains = self.parse_mandatory()
        self.forbidden_domains = self.parse_forbidden()

        self.logger = logHandler.Logger(name=__name__)

    def parse_mandatory(self) -> list:
        """

        @return: a list of Domain instances
        """
        mandatories = []

        for element in self.rule_def['CONDITION']['mandatory']:
            domain = Domain()

            splitted_element = element.split(',')
            if len(splitted_element) == 2:
                domain.name = splitted_element[0].strip()
                domain.ival = float(splitted_element[1].strip())
            elif len(splitted_element) == 1:
                domain.name = splitted_element[0].strip()
                domain.ival = self.co_ival

            mandatories.append(domain)
                        
        return mandatories
        
    def parse_forbidden(self):
        """
        Returns a list of forbidden domain names
        """
        forbidden = []

        if not self.rule_def['CONDITION']['forbidden']:
            return forbidden
        else:
            for element in self.rule_def['CONDITION']['forbidden']:
                domain = Domain()
                splitted_element = element.split(',')
                if len(splitted_element) == 1:
                    domain.name = splitted_element[0].strip()
                forbidden.append(domain)

            return forbidden

    def list_domains(self) -> list:
        """

        @return: list of all domain names in the Rule (both mandatory and forbidden ones)
        """
        return [x.name for x in self.mandatory_domains] + [x.name for x in self.forbidden_domains]
            
    def description(self):
        subtitle = '# Summary for the rule {}'.format(self.name)
        self.logger.info(subtitle)
        self.logger.info(len(subtitle) * '-')
        self.logger.info('Comment: {}'.format(self.comment))
        self.logger.info('Mandatories:')
        for domain in self.mandatory_domains:
            self.logger.info(' - {} ({})'.format(domain.name, domain.ival))
        self.logger.info('Forbidden:')
        if not self.forbidden_domains:
            self.logger.info(' - None')
        else:
            for domain in self.forbidden_domains:
                self.logger.info(' - {}'.format(domain.name))
        self.logger.info('')

    def jsonify_mandatories(self):
        mandatories = []
        for domain in self.mandatory_domains:
            mandatories.append(
                {
                    "name": domain.name,
                    "evalue": domain.ival,
                    "color": None
                }
            )

        return mandatories

    def jsonify_forbidden(self):
        if not self.forbidden_domains:
            return [
                {
                    "name": "None",
                    "color": "None"
                }
            ]

        else:
            forbidden = []
            for domain in self.forbidden_domains:
                forbidden.append(
                    {
                        "name": domain.name,
                        "color": None
                    }
                )

            return forbidden

    def jsonify(self):
        json_rule = {
                "mandatories": self.jsonify_mandatories(),
                "forbidden": self.jsonify_forbidden()
                }

        return json_rule
        

class Domain:
    def __init__(self, name=None, ival=None):
        self.name = name
        self.ival = ival
