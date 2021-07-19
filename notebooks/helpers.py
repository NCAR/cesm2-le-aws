import os
import random
import shutil
from functools import reduce
from operator import mul
from pathlib import Path

import numpy as np
import xarray as xr
from distributed.utils import format_bytes
from tqdm.auto import tqdm

random.seed(42)


def print_ds_info(ds, var):
    """Function for printing chunking information"""
    dt = ds[var].dtype
    itemsize = dt.itemsize
    chunk_size = ds[var].data.chunksize
    size = format_bytes(ds.nbytes)
    _bytes = reduce(mul, chunk_size) * itemsize
    chunk_size_bytes = format_bytes(_bytes)

    print(f'Variable name: {var}')
    print(f'Dataset dimensions: {ds[var].dims}')
    print(f'Chunk shape: {chunk_size}')
    print(f'Dataset shape: {ds[var].shape}')
    print(f'Chunk size: {chunk_size_bytes}')
    print(f'Dataset size: {size}')


def zarr_store(
    experiment,
    component,
    frequency,
    forcing_variant,
    variable,
    write=False,
    dirout='/glade/scratch/mgrover/data/lens2-aws',
):
    """ Create zarr store name/path
    """
    path = f'{dirout}/{component}/{frequency}/cesm2LE-{experiment}-{forcing_variant}-{variable}.zarr'
    if write and os.path.exists(path):
        shutil.rmtree(path)
    print(path)
    return path


def save_data(ds, store):
    try:
        ds.to_zarr(store, consolidated=True, mode='w')
        del ds
    except Exception as e:
        print(f'Failed to write {store}: {e}')


def process_variables(
    col,
    variables,
    component,
    stream,
    experiment,
    date_range=None,
    verbose=False,
):
    query = dict(
        component=component,
        stream=stream,
        variable=variables,
        experiment=experiment,
    )
    if date_range:
        query['date_range'] = date_range
    subset = col.search(**query)
    if verbose:
        print(
            subset.unique(
                columns=[
                    'variable',
                    'component',
                    'stream',
                    'experiment',
                    'date_range',
                ]
            )
        )
    return subset, query


def enforce_chunking(datasets, chunks, field_separator):
    """Enforce uniform chunking"""
    dsets = datasets.copy()
    choice = random.choice(range(0, len(dsets)))
    for i, (key, ds) in enumerate(dsets.items()):
        c = chunks.copy()
        for dim in list(c):
            if dim not in ds.dims:
                del c[dim]
        ds = ds.chunk(c)
        keys_to_delete = ['intake_esm_dataset_key', 'intake_esm_varname']
        for k in keys_to_delete:
            del ds.attrs[k]
        dsets[key] = ds
        variable = key.split(field_separator)[-1]
        print_ds_info(ds, variable)
        if i == choice:
            print(ds)
        print('\n')
    return dsets


def get_grid_vars(ds, variables):
    coord_vars = [
        vname
        for vname in ds.data_vars
        if 'time' not in ds[vname].dims or 'bound' in vname
    ]
    ds_fixed = ds.set_coords(coord_vars)
    grid_vars = list(ds_fixed.drop_dims('time').coords.keys())
    return grid_vars


def create_grid_dataset(sample_file, variables, vars_to_drop=None):
    ds = xr.open_dataset(sample_file, decode_times=False)
    grid_vars = get_grid_vars(ds, variables)
    grid = ds.set_coords(grid_vars)[grid_vars]
    if vars_to_drop:
        to_drop = {vname for vname in vars_to_drop if vname in grid.coords}
        grid = grid.drop(list(to_drop))
    grid.attrs = {}
    return grid


def fix_time(
    ds,
    start,
    end,
    freq,
    time_bounds_dim,
    calendar='noleap',
    generate_bounds=True,
    instantaneous=False,
):
    ds = ds.sortby('time').copy()
    attrs = ds.time.attrs
    encoding = ds.time.encoding
    bounds_name = ds.time.attrs['bounds']
    ds[bounds_name].load()
    if generate_bounds:
        times = xr.cftime_range(
            start=start, end=end, freq=freq, calendar=calendar
        )
        bounds = np.vstack([times[:-1], times[1:]]).T
        ds[bounds_name].data = bounds

    if instantaneous:
        ds = ds.assign_coords(time=ds[bounds_name].min(time_bounds_dim))
    else:
        ds = ds.assign_coords(time=ds[bounds_name].mean(time_bounds_dim))
    ds.time.attrs = attrs
    ds.time.encoding = encoding
    ds = ds.set_coords([bounds_name])
    return ds


def inspect_written_stores(dirout, random_sample_size=None):
    faulty_stores = []
    p = Path(dirout)
    stores = list(p.rglob('*/*.zarr'))
    print(f'Total number of discovered zarr stores: {len(stores)}')
    if random_sample_size:
        stores = random.choices(stores, k=random_sample_size)
    for store in tqdm(stores):
        try:
            ds = xr.open_zarr(store.as_posix(), consolidated=True)
            print('\n')
            print(f'store path: {store}')
            print(f'Time range: {ds.time.min().data} --> {ds.time.max().data}')
        except Exception as e:
            faulty_stores.append(store)
            print(e)
    if faulty_stores:
        print(f'Faulty stores: {faulty_stores}')
