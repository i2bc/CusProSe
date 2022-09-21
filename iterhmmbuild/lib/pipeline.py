# -*- coding: utf-8 -*-
import os
import lib.logHandler as logHandler
import lib.external as external
from iterhmmbuild.lib.parameters import Param
import lib.seqio as seqio


class HmmBuilder:
    """

    Container used to build the core pipeline for IterHmmBuilder

    """

    def __init__(self, _input: str, param: Param, outdir: str):
        """

        @param _input: fasta filename
        @param param: Param instance
        @param outdir: output directory
        """

        self.input = _input
        self.param = param
        self.output = None
        self.outdir = outdir
        self.muscle_output = None

    def run(self, is_usearch_on: bool) -> tuple:
        """

        @param is_usearch_on: boolean, True if a clustering is required at the 1st step of the pipeline, False otherwise.
        @return: three filenames:
            - input_for_muscle: the non-redundant fasta file used as input for muscle (i.e. real input of the pipeline)
            - nr_fasta_merged: the non-redundant enriched fasta file
            - hmmbuild.output: the HMM profile built from muscle output
        """
        if is_usearch_on:
            usearch = external.Usearch(_input=self.input, identity=self.param.id, outdir=self.outdir)
            usearch.run()
            input_for_muscle = usearch.output
        else:
            input_for_muscle = self.input

        muscle = external.Muscle(_input=input_for_muscle, outdir=self.outdir)
        muscle.run()

        hmmbuild = external.HmmBuild(_input=muscle.output, name=self.param.hmm_name, outdir=self.outdir)
        hmmbuild.run()

        self.output = hmmbuild.output
        self.muscle_output = muscle.output


class IterHmmBuilder:
    """

    Container used as a pipeline that aims at building and iterativley growing an HMM profile from a first fasta file
    containing seed sequences and a second one containing sequences used to enrich the seeds to grow up the HMM profile.

    Container used to build an hmmbuilder pipeline. Globally speaking, the pipeline takes:
        - as input: a fasta filename (seed sequences)
        - and outputs:
            - the filename of the build HMM profile
            - the filename of the enriched fasta file

    The hmmbuilder pipeline is made of 4 main steps; from seed sequences (X.fasta) given in a fasta file:
    step 1 - use of muscle to align those seed sequences
            (input: X.fasta -> output: X.clw)

    step 2 - use of hmmbuild to create an HMM profile
            (input: X.clw -> output: X.hmm)

    step 3.a - use of hmmsearch to scan user's given sequences against the previously X.hmm profile
            (input1: X.hmm + input2: protdb.fasta -> output: X.domtblout)

    step 3.b - parse X.domtblout to get hit sequences that met criteria (alignment e-values...)
            (input: X.domtblout -> output: X_enriched.fasta)

    """

    def __init__(self, _input: str, input_db: str, param: Param):
        """

        @param _input: seed fasta filename
        @param input_db: name of the fasta to scan against the HMM profile for the enrichment process
        @param param: Param instance
        """
        self.input_hmmbuilder = _input
        self.basename = '.'.join(os.path.basename(_input).split('.')[0:-1])
        self.input_db = input_db
        self.fasta_dict = seqio.get_fasta_dict(fasta_filename=input_db)
        self.param = param
        self.iter_index = 1
        self.outdir_base = self.param.outdirname
        self.convergence_status = Convergence(delta=self.param.delta, max_count=self.param.maxcount)
        self.outdir = None
        self.output_fasta_enriched = None
        self.is_usearch_on = True

        self.output_fasta = None
        self.output_muscle = None
        self.output_hmm = None

        self.logger = logHandler.Logger(name=__name__)

    def run(self):
        while self.convergence_status.is_converged is False:
            self.logger.title('Iteration {}'.format(self.iter_index))

            self.outdir = self.outdir_base + 'iter_' + str(self.iter_index) + '/'
            self.output_fasta_enriched = self.outdir + self.basename + '_enriched_nr.fasta'
            os.makedirs(self.outdir, exist_ok=True)

            self.convergence_status.number_iter_i = self.count_sequence(fasta_filename=self.input_hmmbuilder)

            hmmbuilder = HmmBuilder(_input=self.input_hmmbuilder, param=self.param, outdir=self.outdir)
            hmmbuilder.run(is_usearch_on=self.is_usearch_on)

            hmmsearch = external.HmmSearch(input_hmm=hmmbuilder.output, input_db=self.input_db, parameters=self.param, outdir=self.outdir)
            hmmsearch.run()

            self.merge_fasta(seed_filename=self.input_hmmbuilder, hits_fasta=hmmsearch.hits.get_fasta(fasta_dict=self.fasta_dict))
            self.convergence_status.number_iter_j = self.count_sequence(fasta_filename=self.output_fasta_enriched)

            self.convergence_status.evaluate()

            self.iter_index += 1
            self.is_usearch_on = False
            self.input_hmmbuilder = self.output_fasta_enriched

        self.logger.title('Final process to build HMM profile')
        self.logger.info('- Input fasta file used as seed: ' + self.input_hmmbuilder)
        self.logger.info('')
        hmmbuilder = HmmBuilder(_input=self.input_hmmbuilder, param=self.param, outdir=self.param.outdirname)
        hmmbuilder.run(is_usearch_on=self.is_usearch_on)

        self.output_fasta = self.param.outdirname + self.param.hmm_name + '_seed.fa'
        os.rename(self.input_hmmbuilder, self.output_fasta)
        self.output_muscle = self.param.outdirname + self.param.hmm_name + '_seed.clw'
        os.rename(hmmbuilder.muscle_output, self.output_muscle)
        self.output_hmm = self.param.outdirname + self.param.hmm_name + '.hmm'
        os.rename(hmmbuilder.output, self.output_hmm)

        self.logger.title('Output files for {} HMM profile'.format(self.param.hmm_name))
        self.logger.info('HMM profile file:   \t{}'.format(self.output_hmm))
        self.logger.info('Fasta seed file:    \t{}'.format(self.output_fasta))
        self.logger.info('Alignment seed file:\t{}'.format(self.output_muscle))
        self.logger.info('')

    def merge_fasta(self, seed_filename: str, hits_fasta: list) -> None:
        """
        Function used to create the enriched fasta file after the hmmsearch scan. This enriched fasta file contains:
            - fasta sequences of hits from hmmsearch
            - seed fasta sequences of the hmm profile used in hmmsearch

        Because some sequences may show some redundancy we want to avoid, usearch is run after the merging the fasta inputs
        into one file.

        @param seed_filename: fasta filename used at the beginning of iteration i
        @param hits_fasta: list of fasta sequences at the end of iteration i
        @return: None
        """

        output_tmp = self.output_fasta_enriched + '.tmp'
        with open(output_tmp, 'w') as outfile:
            with open(seed_filename) as infile:
                for line in infile:
                    outfile.write(line)
            for hit_fasta in hits_fasta:
                outfile.write(hit_fasta)

        usearch = external.Usearch(_input=output_tmp, identity=self.param.id, outdir=self.outdir)
        usearch.run()

        os.remove(output_tmp)
        os.rename(usearch.output, self.output_fasta_enriched)

    @staticmethod
    def count_sequence(fasta_filename: str) -> int:
        """

        @param fasta_filename: name of the fasta file
        @return: the number of sequences in fasta_filename
        """
        seq_number = 0
        with open(fasta_filename, 'r') as fasta_file:
            for line in fasta_file:
                if line.startswith('>'):
                    seq_number += 1

        return seq_number


class Convergence:
    """

    Container used to deal with the convergence status between input and enriched fasta files.

    """
    def __init__(self, delta=1, max_count=3):
        """

        @param delta: difference in sequences number used to consider a non-significant change between between compared fasta files
        @param max_count: maximum number of times a non-significant change (delta) is accepted before considering a convergence
        """
        self.number_iter_i = None
        self.number_iter_j = None
        self.is_converged = False
        self.delta = delta
        self.max_count = max_count
        self.counter = 0

        self.logger = logHandler.Logger(name=__name__)

    def evaluate(self):
        """

        @return: None
        """
        self.logger.info('')
        self.logger.info('Evaluating Convergence:')
        self.logger.info(' - Sequence number before: ' + str(self.number_iter_i))
        self.logger.info(' - Sequence number after: ' + str(self.number_iter_j))

        number_diff = self.number_iter_j - self.number_iter_i

        if abs(number_diff) <= self.delta:
            self.counter += 1
            self.logger.info('')
            self.logger.info('The difference in sequence number is equal to {}, incrementing convergence counter to {}'.format(str(self.delta), str(self.counter)))
        elif number_diff < 0:
            self.counter += 1
            self.logger.info('')
            self.logger.info('The difference in sequence number is negative, incrementing convergence counter to {}'.format(str(self.counter)))

        if self.counter > self.max_count:
            self.is_converged = True
            self.logger.info('')
            self.logger.info('The convergence counter reached its maximum {}, no more iteration.'.format(str(self.counter)))
        elif self.number_iter_j - self.number_iter_i == 0:
            self.is_converged = True
            self.logger.info('')
            self.logger.info('No new sequences have been found, no more iteration.')

        if not self.is_converged:
            self.logger.info('')
            self.logger.info('Convergence criteria not reached, going for a new iteration.')
