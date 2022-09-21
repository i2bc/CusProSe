# IterHMMBuild usage guideline
<div class="admonition tip">
    <p class="first admonition-title">
        Tip
    </p>
    <p>
    To guide the user, input data examples can be found in <code>cusProSe/iterhmmbuild/datas/</code>:
    <pre style="line-height: 15px;"><b>cusProSe/iterhmmbuild/datas/</b>
    ├── inputs
    │   ├── A.fa
    │   ├── KS.fa
    │   └── PP.fa
    └── mgg_70-15_8.fasta
    </pre>

    All fasta files in the <code>inputs/</code> directory contain sequences of three different protein domains. There is also the <i>magnaporthe orizae</i> proteome (<code>mgg_70-15_8.fasta</code>) that will be used as the protein database for the examples below.
    </p>
</div>

## Quick start examples
#### Build a single HMM profile
<div>
Command to build a single HMM profile from the <i>magnaporthe orizae</i> proteome and representative of the A domain sequences:
```bash
iterhmmbuild -fa inputs/A.fa -protdb mgg_70-15_8.fasta
```
</div>

#### Build an HMM profile database
<div>
Command to build an HMM profile database specific to the <i>magnaporthe orizae</i> proteome with each profiles representative of the domain sequences present in the directory `inputs/`:
```bash
iterhmmbuild -fa inputs/ -protdb mgg_70-15_8.fasta
```
</div>

<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>
    Please note that the user can also create an HMM profile database from a set of individual HMM profiles through the command <code class="io">create_hmmdb</code>. Those HMM profiles must be placed in a unique directory that is given as an input.
    </p>
    <p>
    For instance, let's say we have the following directory containing three HMM profiles:
        <pre style="line-height: 15px;"><b>my_hmm_dir/</b>
        ├── A.hmm
        ├── KS.hmm
        └── PP.hmm
        </pre>
    Then the following command will generate an HMM profile database (that is a simple concatenation of the three HMM profiles) called <code class="io">mydb.hmm</code> in an output directory named <code class="io">databases/</code>: 
    </p>
    <p>
    <code class="inside">create_hmmdb -hmmdir my_hmm_dir/ -dbname mydb.hmm -outdir databases/</code>
    </p>
</div>

#### Command line and parameters
As illustrated by the commands above, two arguments are mandatory for IterHMMBuild: `-fa` and `-protdb`.

<ul class="myul">
<li>
The input following <code>-fa</code> can be either a fasta file with at least one protein sequence OR a directory location where multiple individual fasta files are stored. The former can be used when the user wants to build a single HMM profile representative of the sequence(s) given as input. The latter should be used when the user wants to build a set of HMM profiles concatenated into an HMM profile database, with each HMM profile being representative of each related fasta files present in the directory given as input.
</li>
<li>
The input following <code>-protdb</code> is a fasta file of the protein database used to enrich initial protein sequence(s) of interest.
</li>
</ul>

Help about the usage of IterHMMBuild and its parameters can be shown with the following command: `iterhmmbuild -h
`
<pre class="parameters">usage: iterhmmbuild [-h] -fa [FA] -protdb [PROTDB] [-name [NAME]] [-out [OUT]] [-id ID] 
                    [-cov COV] [-cval CVAL] [-ival IVAL] [-acc ACC] [-delta DELTA]
                    [-maxcount MAXCOUNT]

Iterative building of hmm profiles

optional arguments:
  -h, --help          show this help message and exit
  -fa [FA]            Fasta file of sequence(s) used as first seed or directory containing such files
  -protdb [PROTDB]    Sequences used to learn the hmm profile (fasta format)
  -name [NAME]        Name for the HMM profile (fasta name by default).
  -out [OUT]          Output directory
  -id ID              Sequence identity threshold to remove redundancy in seeds&apos;sequences (0.9)
  -cov COV            Minimum percentage of coverage alignment between hmm hit and hmm profile (0.0)
  -cval CVAL          HMMER conditional e-value cutoff (0.01)
  -ival IVAL          HMMER independant e-value cutoff (0.01)
  -acc ACC            HMMER mean probability of the alignment accuracy between each residues of the target and the 
                      corresponding hmm state (0.6)
  -delta DELTA        Convergence criteria: difference in the number of sequences found between two consecutive iterations            
                      to consider a non-significant change between between two consecutive iterations (1)
  -maxcount MAXCOUNT  Convergence criteria: maximum number of times a non-significant change (conv_delta) is accepted before
                      considering a convergence (3)
</pre>

## Output of IterHMMBuild
After running IterHMMBuild an output directory will be generated in the following generic format: 
`iterhmmbuild_year-month-day_hour-min-sec/`

#### Output from the generation of a single HMM profile
The output directory generated from the [command run in the quick start examples](#build-a-single-hmm-profile) will have the following architecture:

<pre><b>iterhmmbuild_2020-10-29_13-13-04/</b>
├── A.hmm
├── A_seed.clw
├── A_seed.fa
├── info.log
├── <b>iter_1/</b>
├── <b>iter_2/</b>
├── <b>...</b>
└── <b>iter_6/</b>
</pre>

The three main files of interest are:
<table class="t-description">
    <tr>
        <td class="t-data"><b>A.hmm</b></td> 
        <td class="t-data">Final HMM profile</td> 
    </tr>
    <tr>
        <td class="t-data"><b>A.seed.clw</b></td> 
        <td class="t-data">Final sequences used to build A.hmm</td> 
    </tr>
    <tr>
        <td class="t-data"><b>A.seed.fa</b></td> 
        <td class="t-data">Multiple alignment (clustal W format) of A_seed.fa</td> 
    </tr>
</table>

`info.log` is a log summary of the computation. The subdirectories `iter_i/` contain files obtained at each iteration and are described in section <a href="./ihb_introduction.html#outputs">Overall procedure</a>.

#### Output from the generation of an HMM profile database
The output directory generated from the [command run in the quick start examples](#build-an-hmm-profile-database) will be a list of subdirectories such as the output described above. You will find at its root the file `hmm_database.hmm`, a concatenation of the HMM profiles of protein domains used as inputs. 

<pre><b>iterhmmbuild_2021-03-02_12-39-38</b>
├── hmm_database.hmm
├── info.log
├── <b>A</b>
│   ├── A.hmm
│   ├── A_seed.clw
│   └── A_seed.fa
├── <b>KS</b>
│   ├── KS.hmm
│   ├── KS_seed.clw
│   └── KS_seed.fa
└── <b>PP</b>
    ├── PP.hmm
    ├── PP_seed.clw
    └── PP_seed.fa
</pre>