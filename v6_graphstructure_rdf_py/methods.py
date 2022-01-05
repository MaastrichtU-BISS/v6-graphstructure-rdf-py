""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""
import time

from pandas.core.frame import DataFrame
import rdflib
import pandas as pd

from vantage6.tools.util import info, warn


def master(client, data, *args, **kwargs):
    """Master algoritm.

    Requests each node to figure out its underlying structure and send it back
    to the master, which takes an intersection and union of those structures
    and returns them to the researcher.
    """

    # get all organizations (ids) that are within the collaboration
    # FlaskIO knows the collaboration to which the container belongs
    # as this is encoded in the JWT (Bearer token)
    organizations = client.get_organizations_in_my_collaboration()
    ids = [organization.get("id") for organization in organizations]

    # The input fot the algorithm is the same for all organizations
    # in this case
    info("Defining input parameters")
    input_ = {
        "method": "get_structure",
    }

    # create a new task for all organizations in the collaboration.
    info("Dispatching node-tasks")
    task = client.create_new_task(
        input_=input_,
        organization_ids=ids
    )

    # wait for node to return results. Instead of polling it is also
    # possible to subscribe to a websocket channel to get status
    # updates
    info("Waiting for resuls")
    task_id = task.get("id")
    task = client.get_task(task_id)
    while not task.get("complete"):
        task = client.get_task(task_id)
        info("Waiting for results")
        time.sleep(1)

    info("Obtaining results")
    results = client.get_results(task_id=task.get("id"))
    info(results)

    # To be able to do set operations
    result_sets = [set[res] for res in results]

    unionset = set()
    interset = set()
    # union and intersect the sets to create a graph with all and common data
    # elements respectively
    for res in result_sets:
        unionset = unionset.union(res)
        interset = interset.intersection(res)

    return {'union': unionset, 'intersect': interset}

def RPC_get_structure(data: rdflib.Graph, *args, **kwargs):
    """RPC_get_structure.

    Get the structure of the graph held in this node. Currently does not send
    labels.
    """
    info(f"Getting graph structure from graph with {len(data)} triples")
    classes = data.query("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?classUri
        WHERE {
            ?instance rdf:type ?class.
        }
    """)

    info(f"Got {len(classes)} classes")

    # We don't want duplicate things by accident
    results = set()

    # Get outgoing relations for each of the classes
    for c in classes:
        classUri = c.classUri
        if not (classUri.startswith("http://www.w3.org/1999/02/22-rdf-syntax-ns#") | 
                        classUri.startswith("http://www.w3.org/2002/07/owl#") | 
                        classUri.startswith("http://www.w3.org/2000/01/rdf-schema#")):
            relations = data.query("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                SELECT DISTINCT ?p ?o
                WHERE {
                    ?instances rdf:type <%s> .
                    ?instances ?p ?relatedInstance .
                    ?relatedInstance rdf:type ?o .
                }
            """ % classUri)

            # Add a link of class --p--> o to the results
            for rel in relations:
                results.add((classUri, rel.p, rel.o))

    # send all the 'triples' to the master (cast to list as that should be a 
    # doable for decoding)
    return list(results)
