<h1 align="center">
  <br>
  <a href="https://vantage6.ai"><img src="https://github.com/IKNL/guidelines/blob/master/resources/logos/vantage6.png?raw=true" alt="vantage6" width="400"></a>
</h1>

<h3 align=center> A privacy preserving federated learning solution</h3>

--------------------

# v6_graphstructure_rdf_py
This algoithm is part of the [vantage6](https://vantage6.ai) solution. Vantage6 allowes to execute computations on federated datasets. This repository provides a boilerplate for new algorithms.

This specific algorithm assumes nodes with a single `.ttl` file as it's 'database'.
This triples file is analyzed and the underlying graph structure is computed and
combined with graphs from other nodes. The graphs are intersected and unioned
in order to get a good understanding of what the underlying data looks like 
without any prior knowledge.

## To download this locally for development
First clone the repository.
```bash
# Clone this repository
git clone https://github.com/jaspersnel/v6-graphstructure-rdf-py
```

## Publishing for real-world use

### Building the image
If everything has been entered correctly in the setup stage, you should only have to build the image and push it to docker hub to be able to use it:

```bash
docker build -t your_username/algorithm_name .
docker push your_username/algorithm_name
```

## Read more
See the [documentation](https://docs.vantage6.ai/) for detailed instructions on how to install and use the server and nodes.

------------------------------------
> [vantage6](https://vantage6.ai)