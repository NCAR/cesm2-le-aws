# Zarrification Process Overview

This directory contains the notebooks/scripts required to convert from netCDF to Zarr. These are the steps to generating these stores:

## Step 1 - Catalog the Data on NCAR HPC (GLADE file system)
You will need to run the `build_glade_catalog.ipynb` notebook first, which generates the CESM2-LE Glade catalog. It is recommended that your maximize the number of cores when running this notebook, so make sure to try to access as many CPUs as possible on the JupyterHub when running this.

## Step 2 - Change your `config.yml` to match the desired output
Currently, all of the variables for all of the components are included in the configuration file... this will likely take a very long time, and it is recommended you comment the components/frequencies you do not want to process.

## Step 3 - Zarrify your Data!
You will want to log back onto the JupyterHub, and request a single node with a small amount of memory (~10 GB), so that when you spin up your Dask Cluster, you can request a large number of workers. When producing the monthly output, you will want to request a **large number of smaller memory workers**, whereas the higher frequency output (larger Zarr stores) will require a **as many workers/memory as possible**.

## Step 4 - Upload to Stratus
Once you generate your Zarr stores, you can upload your data to stratus. Make sure to set your configuration files correctly on NCAR HPC, and upload to the `ncar-cesm2-lens` bucket, in the corresponding component/frequency directory.

Once you upload your data, regenerate the AWS CESM2-LE catalog using the `build_aws_catalog.py` script.

## Step 5 - Rebuild the Docs
You will now need to go into the `/docs` directory, and rerun the `model_documentation.ipynb` notebook, which will update the table with the new data. Commit your changes, push to the repo, and you're done!