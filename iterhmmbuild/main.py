import os
import glob
import sys
from shutil import copyfile, rmtree

import lib.logHandler as logHandler
from iterhmmbuild.lib import parameters, pipeline


def main():
    param = parameters.Param(args=parameters.get_args())
    logger = logHandler.Logger(name='main', outpath=param.outdirname)
    param.description()

    if os.path.isdir(param.fasta_fname):
        fasta_filenames = (x for x in glob.glob(param.fasta_fname + '/' + '*.fa'))
        if fasta_filenames:
            run_iter_ondir(fasta_filenames=fasta_filenames, param=param, logger=logger)
    else:
        iterhmmbuilder = pipeline.IterHmmBuilder(_input=param.fasta_fname, input_db=param.protdb, param=param)
        logger.title("Running iterHmmBuilder")
        iterhmmbuilder.run()


def run_iter_ondir(fasta_filenames, param, logger):
    hmm_outputs = []
    outdirname_base = param.outdirname
    for fasta_filename in fasta_filenames:
        param.hmm_name = os.path.basename(fasta_filename).split('.')[0]
        param.outdirname = outdirname_base + param.hmm_name + '/'

        iterhmmbuilder = pipeline.IterHmmBuilder(_input=fasta_filename, input_db=param.protdb, param=param)
        logger.title("Running iterHmmBuilder")
        iterhmmbuilder.run()
        hmm_outputs.append(iterhmmbuilder.output_hmm)

    hmmdir = outdirname_base + 'hmmdir/'
    os.makedirs(hmmdir, exist_ok=True)
    [copyfile(src, hmmdir + os.path.basename(src)) for src in hmm_outputs]
    cmd = 'create_hmmdb ' + '-hmmdir ' + outdirname_base + 'hmmdir/' + ' -outdir ' + outdirname_base
    os.system(cmd)
    rmtree(hmmdir)


if __name__ == '__main__':
    sys.exit(main())
