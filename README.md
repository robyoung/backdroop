# So what is this thing?

The idea of using JSON schemas to validate incoming data has been talked about
quite a bit. It has been suggested that they have the potential to be really 
useful at a couple of points in backdrop and elsewhere. I wanted to test 
whether the theory was actually as good as it seemed. This repo implements a 
simplified backdrop within our current model but uses JSON schemas in a few
places.

There are a few ways that better defining what we expect and what we will
provide would make documentation and conversations with 3rd parties much
easier. I'm not tackling that point at all here. This repo is purely about how
they could help us technically.

# Where are JSON schemas used?

- There is a data set specific schema
- There is a generic query schema

## As records come in
- Records are validated against the data set schema
- The schema is used to create the data set if it doesn't exist
  - Adds relevant indexes

## As queries come in
- The query schema is used to validate whether a query is well formed
- The parsed query is validated against the data set schema
  - Fails if fields are used that are not present in the schema

# Sounds interesing, where should I start?

The flask webapp is in `backdrop.webapp` so that is probably the best place
to start.

Run the tests with `nosetests -s --with-nosetests`

Run the app with `python start.py`

# Did anything else fall out in the doing?

Yes.

## Better separation of concerns
- A module per major stage in the process
  - Access to data set metadata - `models`
  - Incoming data processing and validation  - `data`
  - Query parsing and validation - `query`
  - Building output results - `results`
  - Storage engines - `storage`
- Storage engine code just does storage engine specific stuff
  - Small API for what a storage engine needs to do
    - create a data set
    - add records
    - query
  - The storage engine handles all of it's querying
    - nothing bleeding out into other layers
  - The storage engine doesn't do any of the respone building (woot yay fuck yea)
- Each module has a small number of entry points
  - explicitly documented with `__all__`

## Actions on data implemented as a series of functions
- Easy to see the stages the data goes through
- Easy to test and refactor stages in isolation
- Easy to reorder, add or remove stages

## Side effects restricted to a small number of places
- As much logic as possible done in pure functions
- Doctests describe how functions should work where functions are defined

# What is missing?
- Error responses could, with this model, be *much* richer. This isn't done.
- Authentication and authorisation is completely ignored
- Response building is much simplified (no hierarchical results)
- Some things that should be concrete data types are implemented as dicts for ease
  - There should be a Query type
  - There should be a DataSet type
  - Maybe there should be a Record type (not sure about this one)

# What should we do?
- SCHEMA ALL THE THINGS!
