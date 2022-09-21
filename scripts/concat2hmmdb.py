import sys
import argparse
import prosecda.lib.seqio as seqio


def main():
    args = get_arguments()
    hmmdir = args.hmmdir if args.hmmdir[-1] == '/' else args.hmmdir + '/'
    outpath = args.outdir if args.outdir[-1] == '/' else args.outdir + '/'
    dbname = outpath + args.dbname

    hmm_profiles = seqio.get_files(directory=hmmdir, extension='.hmm')

    if hmm_profiles:
        seqio.concat_file(outputfile=dbname, inputfilelist=hmm_profiles)


def get_arguments():
    """

    Returns all arguments given as inputs

    """
    parser = argparse.ArgumentParser(description='Creating an HMM profile database data from multiple HMM profiles')
    parser.add_argument("-hmmdir", required=True, nargs="?",
                        help="Directory containing HMM profiles")
    parser.add_argument("-dbname", required=False, nargs="?", default='hmm_database.hmm',
                        help="Name for the output HMM database.")
    parser.add_argument("-outdir", required=False, nargs="?", default='./', type=str,
                        help="Output directory")

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    sys.exit(main())
