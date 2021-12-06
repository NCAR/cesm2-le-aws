# NCAR CESM2 Large Ensemble Cloud-Optimized Dataset

Examples of analysis of [CESM2-LE data](https://registry.opendata.aws/ncar-cesm2-lens/) publicly available on Amazon S3 (us-west-2 region) using xarray and dask.

## ESM Catalog
The main catalog URL is:

https://raw.githubusercontent.com/NCAR/cesm2-le-aws/main/intake-catalogs/aws-cesm2-le.json

This catalog is an [ESM collection](https://github.com/NCAR/esm-collection-spec) catalog. The data is stored in [Zarr](https://github.com/zarr-developers/zarr) format and meant to be opened with [Xarray](http://xarray.pydata.org/en/latest/).

## Requirements

Using this catalog requires the following package versions:

- [Intake-esm](https://github.com/intake/intake-esm)

## Reference Documentation

- For details about intake-esm API, see the [reference documentation](https://intake-esm.readthedocs.io/en/latest)
- [CESM2-LE on AWS Site](https://doi.org/10.26024/y48t-q717)

## Source Code for CESM2-LE on AWS Site

The source code for [https://doi.org/10.26024/y48t-q717](https://doi.org/10.26024/y48t-q717) resides in the [docs directory](./docs) of this repository.

The site is built with [JupyterBook](https://jupyterbook.org/intro.html).

To build the site locally, please use [conda](https://docs.conda.io/) to set up a build environment with all dependencies.

```bash
git clone https://github.com/NCAR/cesm2-le-aws
```

Set up your a conda environment:

```bash
conda env create -f docs/environment.yml
conda activate cesm2-le-aws-site
```

You can then build the site with:

```bash
jupyter-book build docs/
```