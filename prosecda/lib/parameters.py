# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:41:15 2020

@author: nicolas
"""
import os
import argparse
import datetime
import prosecda.lib.seqio as seqio
import lib.logHandler as logHandler

date = datetime.datetime.now()
date = '_'.join(str(date).split('.')[0].split()).replace(':', '-')


class Param:
    """

    Wrapper of all input files and arguments

    """
    def __init__(self, args):
        """

        @param args: return of argparse.ArgumentParser.parse_args()
        """
        self.proteome_filename = args.proteome
        self.fasta_dict = seqio.read_fasta(sequences=self.proteome_filename)
        self.hmmdb = args.hmmdb
        self.yamlrules = args.rules

        outpath = args.out if args.out[-1] == '/' else args.out + '/'
        default_mainname = 'prosecda_' + date + '/'
        self.outdirname = outpath + default_mainname
        os.makedirs(self.outdirname, exist_ok=True)

        self.score_co = args.score
        self.cov = args.cov
        self.cval = args.cevalue
        self.ival = args.ievalue
        self.acc = args.acc
        self.nopdf = args.nopdf
        # self.rules = rules.parse_rules(filename=self.yamlrules, score_co=self.score_co)

        self.logger = logHandler.Logger(name=__name__)

    def description(self):
        """

        A formatted string describing all key index positions stored.

        Returns:
            object: str

        """
        self.logger.info('')
        self.logger.info('# Summary of input files used parameters:')
        self.logger.info('- Output of hmmscan (.domtblout): {}'.format(self.hmmdb))
        self.logger.info('- Proteome (.fasta): {}'.format(self.proteome_filename))
        self.logger.info('- Rules (.yaml): {}'.format(self.yamlrules))
        self.logger.info('- Output path: {}'.format(self.outdirname))
        self.logger.info('- HMM coverage: {}'.format(self.cov))
        self.logger.info('- i-Evalue cutoff for domain match: {}'.format(self.ival))
        self.logger.info('- c-Evalue cutoff for domain match: {}'.format(self.cval))
        self.logger.info('- HMMER accuracy: {}'.format(self.acc))
        self.logger.info('- --nopdf: {}'.format(self.nopdf))
        self.logger.info('')


def get_arguments():
    """

    Returns all arguments given as inputs

    """
    parser = argparse.ArgumentParser(description='Search proteins matching rules.')
    parser.add_argument("-proteome", required=True, nargs="?",
                        help="Proteome file (.fasta) ")
    parser.add_argument("-hmmdb", required=True, nargs="?",
                        help="HMM profile database")
    parser.add_argument("-rules", required=True, nargs="?",
                        help="Rules'file (.yaml)")
    parser.add_argument("-out", required=False, nargs="?", default='./', type=str,
                        help="Output directory")

    parser.add_argument("-cov", required=False, default=0.0, type=float,
                        help="Minimum ratio between the length of the HMM profile stretch that matches a sequence and the overall length of the HMM profile. (0.0)")
    parser.add_argument("-cevalue", required=False, default=0.01, type=float,
                        help="HMMER conditional e-value cutoff (0.01)")
    parser.add_argument("-ievalue", required=False, default=0.01, type=float,
                        help="HMMER independant e-value cutoff (0.01)")
    parser.add_argument("-score", required=False, default=3.0, type=float,
                        help="HMMER score cutoff (3.0)")
    parser.add_argument("-acc", required=False, default=0.6, type=float,
                        help="HMMER mean probability of the alignment accuracy between each residues of the target and the corresponding hmm state (0.6)")
    parser.add_argument("--nopdf", required=False, action='store_true', help="Deactivate the generation of the pdf results (False)")
    args = parser.parse_args()

    return args
