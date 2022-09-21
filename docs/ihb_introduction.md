# IterHMMBuild overall procedure
<figure class="fig-iterhmmbuild">
    <img src="./img/iterhmmbuild_pipeline_v2.png"
      alt="IterHMMBuild pipeline overview.">
    <figcaption>
<b>Figure 2: Pipeline overview of IterHMMBuild</b> 
    </figcaption>
</figure>

IterHMMBuild is an iterative search method based on the hmmer program, the aim of which is to provide users with a representative HMM protein profile of interest constructed by an iterative enrichment process starting from a small initial set of related protein sequences.

The IterHMMBuild procedure starts building an HMM profile from either a set of related protein sequences or a single query sequence. This initial profile is then used to identify homologous sequences in any user-specified protein sequence database. If sequences are found, they are added to the initial query sequences and a new HMM profile model is built. This process is repeated until no new sequences are found (i.e. convergence is reached).

## Inputs
Two inputs are required for IterHMMBuild.

The first input is either a fasta file with at least one protein sequence  (<a href="#iterhmmbuild-overall-procedure">Figure 2</a>) OR a directory location where multiple individual fasta files are stored (<a href="./index.html#fig-1">Figure 1</a>). In the first case, the output will contain an HMM profile representative of the sequences in the fasta file given as input; if a directory is given as input then the HMM profile in the output will be a concatenation of HMM profiles, each corresponding to the fasta files present in the directory.

The second input is a fasta file of protein database used to enrich initial protein sequence(s) of interest.

## HMM building step
<figure>
<img class="align-right" src="./img/step_hmmbuilding_enrichment.png">
</figure>
<p>
The HMM building is a two-step procedure: a multiple sequence alignment is performed on the input sequences using muscle and the hmmbuild command from hmmer is then used to build the HMM profile from this alignment. However, note that at the first iteration the usearch command is performed on the input sequences to ensure that thoses sequences share no more than 90% (default value) of identity.
</p>

## Sequence enrichment step
The previously built HMM profile is searched against the protein database given as input using the hmmsearch command from hmmer. All matching sequences with a E-values<sup>a</sup> less than 0.01 (default value) and an expected accuracy per residue of the alignment<sup>b</sup> above or equal to 0.6 (default value) are retrieved. Those sequences are then merged to the initial input sequences. To ensure that sequences are not redundant, usearch is applied with a threshold identity value of 0.90.

<div class="admonition note">
    <p class="first admonition-title">
        Note
    </p>
    <ul class="last">
        <li class="note-ref"><sup>a</sup> Both conditional and independent E-values from hmmer are evaluated</li>
        <li class="note-ref"><sup>b</sup> Please see the <a href="http://eddylab.org/software/hmmer3/3.1b2/Userguide.pdf">hmmer documentation</a> for more details about the accuracy</li>
    </ul>
</div>

## Convergence
Basically, the convergence is reached when the number of sequences at iteration i+1 (Nseq<sub>i+1</sub>) is strictly equal to the number of sequences at iteration i (Nseq<sub>i</sub>). However, because the number of new sequences found after multiple consecutive iterations can be really low, or even negative, a counter is also used to evaluate the convergence status in order to prevent unnecessay iterations (i.e. iterations that will increase the computation time without significantly enrich the number of new sequences). This counter is incremented each time the difference between Nseq<sub>i+1</sub> and Nseq<sub>i</sub> is negative or equal to 1 (default value). The convergence is then also reached when the value of this counter is equal to 3 (default value).


## Outputs
An example output is as shown below:

<pre><b>iterhmmbuild_2020-10-29_13-13-04/</b>
├── X.hmm
├── X_seed.clw
├── X_seed.fa
├── info.log
├── <b>iter_1</b>
│   ├── X_enriched_nr.fasta
│   ├── X_nr.clw
│   ├── X_nr.domtblout
│   ├── X_nr.fa
│   └── X_nr.hmm
├── <b>...</b>
└── <b>iter_6</b>
    ├── X_enriched_nr.clw
    ├── X_enriched_nr.domtblout
    ├── X_enriched_nr.fasta
    └── X_enriched_nr.hmm
</pre>

The table below describes the content of the output directory:

<table class="mytable">
    <tr>
        <th class="t-header">File name</th>
        <th class="t-header">Description</th>
    </tr>
    <tr>
        <td class="t-data">X.hmm</td> 
        <td class="t-data">Final HMM profile</td> 
    </tr>
    <tr>
        <td class="t-data">X_seed.fa</td> 
        <td class="t-data">Final sequences used to build X.hmm</td> 
    </tr>
    <tr>
        <td class="t-data">X_seed.clw</td> 
        <td class="t-data">Multiple alignment (clustal W format) of X_seed.fa</td> 
    </tr>
    <tr>
        <td class="t-data">info.log</td> 
        <td class="t-data">Log summary of the computation</td> 
    </tr>
    <tr>
        <td class="t-data">iter_1/X_nr.fa</td> 
        <td class="t-data">Non redundant sequences coming from usearch applied on the input X.fa 
        (see <a href="./ihb_introduction.html#hmm-building-step">IterHMMBuild procedure</a>)
        </td>
    </tr>
    <tr>
        <td class="t-data">iter_1/X_nr.clw</td> 
        <td class="t-data">Multiple alignment of sequences in X_nr.fa
        </td>
    </tr>
    <tr>
        <td class="t-data">iter_1/X_nr.hmm</td> 
        <td class="t-data">HMM profile built with X_nr.clw as input
        </td>
    </tr>
    <tr>
        <td class="t-data">iter_1/X_nr.domtblout</td> 
        <td class="t-data">Output file of the hmmsearch command
        </td>
    </tr>
    <tr>
        <td class="t-data">iter_1/X_enriched_nr.fasta</td> 
        <td class="t-data">Non redundant sequences coming from homologous sequences identified
        with hmmsearch and initial sequences in X.fa 
        </td>
    </tr>
</table>
