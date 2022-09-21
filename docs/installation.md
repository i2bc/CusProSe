# Installation

<div class="admonition note">
    <p class="first admonition-title">
        Note
    </p>
    <p class="last">
        CusProSe requires a python version >= 3.7
    </p>
</div>

## External dependencies
CusProSe relies on three external tools: hmmer, muscle and usearch.
The first two can be easily installed from the following commands:

* [hmmer](http://hmmer.org/download.html) (tested with version 3.3)
``` bash
sudo apt install hmmer
```
* [muscle](https://www.drive5.com/muscle/downloads.htm) (tested with version 3.8.1551)
``` bash
sudo apt install muscle
```

For usearch, you first need to download it here:
[usearch](https://www.drive5.com/usearch/download.html) (tested with version v10.0.240)

Next, you will have to rename it and make it accessible from anywhere in your system:
``` bash
# rename to usearch
mv usearchXX.X.XXX_i86xxxx.gz usearch

# make usearch executable
chmod +x usearch

# make usearch easily accessible
mkdir ~/bin
mv usearch ~/bin
```

Finally, copy the following line in your .bashrc file (or .bash_profile for macos users)
``` bash
export PATH=$PATH:~/bin 
```

## Create an isolated environment
Although not indispensable, this step is highly recommended (it will allow you to work on different projects avoiding potential conflicts between different versions of some python libraries).
 
### Install virtualenv
``` python
python3 -m pip install virtualenv
```

### Create a virtual python3 environment
```bash
virtualenv -p python3 my_env
```

### Activate the created environment
```bash
source my_env/bin/activate
```

Once activated, any python library you'll install using pip will be installed solely in this isolated environment.
Every time you'll need to work with libraries installed in this environment (i.e. work on your project), you'll have
to activate it. 

Once you're done working on your project, simply type `deactivate` to exit the environment.

## Download and install the latest release of CusProSe
Click here for the latest release: 
[ ![](./icons/download-flat/16x16.png "Click to download the latest release")](https://github.com/nchenche/cusProSe/releases/latest/)

### Uncompress the archive
If you downloaded the *.zip* file:
```bash
unzip cusProSe-x.x.x.zip
```

If you downloaded the *.tar.gz* file:
```bash
tar xzvf cusProSe-x.x.x.tar.gz
```

### Go to the cusProSe directory
 
```bash
cd cusProSe-x.x.x/
```

### Install CusProSe on your virtual environment
Make sure your virtual environment is activated and type the following command: 

```python
python setup.py install
```

or 
```python
pip install .
```

<div class="admonition tip" style="margin-top: 30px;">
    <p class="first admonition-title">
        Note
    </p>  
    <ul>
    If the installation successfully worked, then typing:
  <li>
  <code>iterhmmbuild</code> should display:
    <pre class="parameters">usage: iterhmmbuild [-h] -fa [FA] -protdb [PROTDB] [-name [NAME]] [-out [OUT]] [-id ID]
                    [-cov COV] [-cval CVAL] [-ival IVAL] [-acc ACC]
    </pre>
  </li>

  <li>
    <code>prosecda</code> should display:
    <pre class="parameters">usage: prosecda [-h] -proteome [PROTEOME] -hmmdb [HMMDB] -rules [RULES] [-out [OUT]] 
                    [-cov COV] [-cevalue CVAL] [-ievalue IVAL] [-score SCORE] [-acc ACC]
                    [--nopdf]
    </pre>
  </li>

  <li>
    <code>create_hmmdb</code> should display:
    <pre class="parameters">usage: create_hmmdb [-h] -hmmdir [HMMDIR] [-dbname [DBNAME]] [-outdir [OUTDIR]]
    </pre>
  </li>
</ul>

</div>
