# -*- coding: utf-8 -*-
# import shutil
import lib.logHandler as logHandler

logger = logHandler.Logger(name=__name__)


def get_fasta_dict(fasta_filename: str = 'name', protein_ids: list = None):
    """

    Parse a protein fasta file to return a dictionary with protein ids as keys and sequences as values.

    @param fasta_filename: fasta filename
    @param protein_ids: optional, list of protein ids to read, ids not in this list will not be considered
    @return: a dictionary (keys=proteins ids, values=sequence)
    """
    fasta_dict = {}
    with open(fasta_filename, 'r') as fasta_file:
        if not protein_ids:
            for line in fasta_file:
                if line.startswith('>'):
                    protein_id = line.split()[0].split('>')[-1]
                    if protein_id not in fasta_dict:
                        fasta_dict[protein_id] = ''
                else:
                    sequence = line.strip().replace('*', '')
                    fasta_dict[protein_id] += sequence
        else:
            for line in fasta_file:
                if line.startswith('>'):
                    protein_id = line.split()[0].split('>')[-1]
                    if protein_id not in protein_ids:
                        continue
                    else:
                        if protein_id not in fasta_dict:
                            fasta_dict[protein_id] = ''
                            continue
                if protein_id in fasta_dict:
                    sequence = line.strip().replace('*', '')
                    fasta_dict[protein_id] += sequence

    return fasta_dict
