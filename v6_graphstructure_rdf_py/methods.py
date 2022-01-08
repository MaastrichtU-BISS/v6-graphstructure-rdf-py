""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""
import time

from pandas.core.frame import DataFrame
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

    info(str(results))

    info("Combining structure results")
    # To be able to do set operations
    result_sets = [set(res['structure']) for res in results]

    unionset = set()
    interset = set()
    # union and intersect the sets to create a graph with all and common data
    # elements respectively
    for res in result_sets:
        unionset = unionset.union(res)
        if len(interset) == 0:
            interset = res
        else:
            interset = interset.intersection(res)

    info("combining URI data")
    uri_data = {k: v for res in results for k, v in res['uri_data'].items()}

    info("Returning data")
    return {'union': list(unionset), 'intersect': list(interset), 'uri_data': uri_data}

def RPC_get_structure(data: pd.DataFrame, *args, **kwargs):
    """RPC_get_structure.

    Get the structure of the graph held in this node.
    """
    info(f"Got {len(data)} links")
    structure = ['type1', 'p', 'type2']
    labels = ['label1', 'labelp', 'label2']
    literals = ['type1', 'p', 'datatype']

    class_data = data[~data['type2'].isna()]
    literal_data = data[~data['datatype'].isna()]

    info("Looking up all classes")
    uri_data = {uri: {'type': 'class'} for uri in class_data['type1'].unique()}
    uri_data = {**uri_data, **{uri: {'type': 'class'} for uri in class_data['type2'].unique()}}
    uri_data = {**uri_data, **{uri: {'type': 'literal'} for uri in literal_data['datatype'].unique()}}

    info("Getting URI metadata")
    for _, row in data.iterrows():
        for col1, col2 in zip(structure, labels):
            if not pd.isna(row[col2]):
                if row[col1] in uri_data:
                    uri_data[row[col1]]['label'] = row[col2]

    info("Returning data")
    return({
        'structure': [tuple(trp) for trp in list(class_data[structure].to_records(index=False))] + [tuple(trp) for trp in list(literal_data[literals].to_records(index=False))],
        'uri_data': uri_data,
    })