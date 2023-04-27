"""
Author : Moontasir Mahmood
Github : munmud
"""

from age import *
import psycopg2
import networkx as nx
from psycopg2 import sql
from typing import Dict, Any

def ageToNetworkx(connection : psycopg2.connect, 
                  GRAPH_NAME : str) -> nx.DiGraph:
    """
    This Function Creates a Directed Graph from AGE Graph db. It will load all the nodes and edges it can find from the age db to networkx

    @Params
    -------

    connection - psycopg2.connect
        A connection object when retruning from psycopg2.connect
    
    GRAPH_NAME - string
        Name of the Graph

    @Returns
    --------
    nx.DiGraph
        A Networkx Directed Graph
    """
    
    # Check if the age graph exists
    with connection.cursor() as cursor:
        query = """
                    SELECT count(*) 
                    FROM ag_catalog.ag_graph 
                    WHERE name='%s'
                """ % (GRAPH_NAME)
        cursor.execute(sql.SQL(query))
        if cursor.fetchone()[0] == 0:
            raise GraphNotFound(GRAPH_NAME)
    
    # Setting up connection to work with Graph
    age.setUpAge(connection, GRAPH_NAME)
    
    # Create an empty directed graph
    G = nx.DiGraph()
    
    # Get all vertices
    with connection.cursor() as cursor:
        query = """
                    SELECT * FROM cypher('%s', 
                    $$ 
                        MATCH (n) 
                        RETURN (n) 
                    $$) as (v agtype);
                """ % (GRAPH_NAME)
        try :
            cursor.execute(query)
            connection.commit()
            for row in cursor:
                G.add_node(row[0].id, 
                           label=row[0].label, 
                           properties=row[0].properties)
        except Exception as ex:
            print(type(ex), ex)

    # Get All edges
    with connection.cursor() as cursor:
        query = """
                SELECT * from cypher(
                    '%s', 
                    $$ 
                        MATCH v=()-[]->() 
                        RETURN v 
                    $$
                ) as (v agtype); 
                """ % (GRAPH_NAME)
        try :
            cursor.execute(query)
            connection.commit()
            for row in cursor:
                G.add_edge(row[0][1].start_id, 
                           row[0][1].end_id, 
                           label=row[0][1].label, 
                           properties=row[0][1].properties)
        except Exception as ex:
            print(type(ex), ex)
    
    return G


def networkxToAge(connection : psycopg2.connect,
                  G : nx.DiGraph,
                  GRAPH_NAME:str) -> None:
    """
    This Function add all the nodes and edges found from a Networkx Directed Graph to Apache AGE Graph Database

    @Params
    -------

    connection - psycopg2.connect
        A connection object when retruning from psycopg2.connect
    
    G - nx.DiGraph
        A Networkx Directed Graph
    
    GRAPH_NAME - string
        Name of the Graph

    @Returns
    --------
    None
    """
    # Setting up connection to work with Graph
    age.setUpAge(connection, GRAPH_NAME)

    mapId={} # Used to map the user id with Graph id
    
    # python dictionary to string
    def dictToStr( property):
        """Converts py dictionary into age query json type"""
        p = "{"
        for x,y in property.items():
            p+= x + " : "
            if type(y) == type({}):
                p+=dictToStr(y)
            else :
                p+= "'"
                p+= str(y)
                p+= "',"
        p = p.removesuffix(',')
        p+= "}"
        return p
    
    def set_vertices(id : int | str, label : str, properties: Dict[str, Any]) -> None:
        """Add a vertices to the graph"""
        with connection.cursor() as cursor:
            query = """
            SELECT * from cypher(
                '%s', 
                $$ 
                    CREATE (v:%s %s) 
                    RETURN v
                $$
            ) as (v agtype); 
            """ % (GRAPH_NAME, label,dictToStr(properties))
            # print(query)
            try :
                cursor.execute(query)
                for row in cursor:
                    mapId[id]=row[0].id
                        
                # When data inserted or updated, You must commit.
                connection.commit()
            except Exception as ex:
                print(type(ex), ex)
                # if exception occurs, you must rollback all transaction. 
                connection.rollback()

    def set_edge(id1 : int | str , id2 : int | str, edge_label: str, edge_properties: Dict[str, Any])->None:
        """Add edge to the graph"""
        with connection.cursor() as cursor:
            query ="""
            SELECT * from cypher(
                '%s', 
                $$ 
                    MATCH (a), (b)
                    WHERE id(a) = %s AND id(b) = %s
                    CREATE (a)-[r:%s %s]->(b)
                    RETURN r
                $$) as (v agtype);
            """ % (
                GRAPH_NAME,
                mapId[id1],
                mapId[id2],
                edge_label, 
                dictToStr(edge_properties)
            )
            try :
                cursor.execute(query)
                connection.commit()
                for row in cursor:
                    # print(row[0].id)
                    pass
            except Exception as ex:
                print('Exception : ',type(ex), ex)
                # if exception occurs, you must rollback all transaction. 
                connection.rollback()


    for node in G.nodes:
        set_vertices(id = node,
                     label=G.nodes[node]['label'],
                     properties=G.nodes[node]['properties'])
    
    for u, v in G.edges:
        set_edge(id1 = u,
                 id2 = v,
                 edge_label=G.edges[u, v]['label'],
                 edge_properties=G.edges[u, v]['properties'])
    
    # print("Successfully Added nodes with id mapped as below\n" , mapId)