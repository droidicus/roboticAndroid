# roboticAndroid
Discord bot for data analytics

# Get a copy of the project
* Clone the repository
* Create a bot account with discord, copy the token that is generated during this process
* Open the `token` file in the root directory with a text editor
* Paste the token copied above and ensure it is on a single line
* Save the `token` file

# Set up environment on a Window 10 system
## Install Miniconda
* See instructions here: https://docs.conda.io/en/latest/miniconda.html
## Base environment setup
```
conda create -n nbstripout
conda activate nbstripout
conda install -c conda-forge nbstripout
```
* Navigate to the cloned repo
```
nbstripout --install
conda deactivate nbstripout
```
## Jupyter Lab environment
```
conda create -n jupyterlab python jupyterlab ipympl widgetsnbextension nodejs ipywidgets
conda activate jupyterlab
set NODE_OPTIONS=--max-old-space-size=4096
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
jupyter labextension install jupyterlab-plotly --no-build
jupyter labextension install plotlywidget --no-build
jupyter labextension install jupyter-matplotlib --no-build
jupyter lab build
set NODE_OPTIONS=
conda deactivate
```
## Discord conda environment
```
conda create -n discord python matplotlib plotly numpy pandas tqdm ipykernel fastparquet python-snappy pylint scipy ipympl
conda activate discord
pip install discord.py
python -m ipykernel install --user --name discord --display-name "Python (discord)"
conda deactivate
```
## Tensorflow environment
* Install `Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017 and 2019` from here: https://support.microsoft.com/help/2977003/the-latest-supported-visual-c-downloads
```
conda create -n tensorflow python tensorflow-gpu tensorflow-hub tensorflow-datasets matplotlib plotly pandas tqdm ipykernel fastparquet python-snappy pylint ipympl pytables h5py
conda activate tensorflow
python -m ipykernel install --user --name tensorflow --display-name "Python (tensorflow)"
conda deactivate
```

```
conda create -n tensorflow python matplotlib plotly pandas tqdm ipykernel fastparquet python-snappy pylint ipympl pytables h5py
conda activate tensorflow
pip install tensorflow tensorflow-hub tensorflow-datasets
python -m ipykernel install --user --name tensorflow --display-name "Python (tensorflow)"
conda deactivate
```

# How to run
## To run the bot to gather data from the server history
* Open the CMD prompt.
* Navigate to the repository clone/copy
```
conda activate discord
python discord.py
conda deactivate
```
## How to launch jupyter lab for data analysis
* Open the CMD prompt
* Navigate to the repository clone/copy
```
conda activate jupyterlab
jupyter lab
```
* Open the Jupyter Lab environment in the browser of your choice
* Open `main.ipynb`
* Ensure that the `discord` python environment is selected
* Run the cells of interest
