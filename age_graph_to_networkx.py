"""
Author: Syed Safi Ullah Shah
GitHubID: safi50 
DiscordID: safi50
"""


import age
from age.exceptions import *
import psycopg2 
from psycopg2 import sql
import networkx as nx
import matplotlib.pyplot as plt


#ESTABLISHING CONNECTION
conn = psycopg2.connect(
    host="localhost", 
    port="5432", 
    dbname="your_db_name", 
    user="your_user_name", 
    password="your_password")

GRAPH_NAME = "your_graph_name"
#Setting Up AGE
age.setUpAge(conn, GRAPH_NAME)



""" Load a graph from Apache AGE into a NetworkX DiGraph object and visualize it.
    This function first checks if the given AGE graph exists in the database.
    If it does, it retrieves all vertices and edges from the graph, and creates a 
    NetworkX DiGraph object with the same structure. """
def load_graph_to_networkx():
    try: 

        # Creating a NetworkX graph
        G = nx.DiGraph() 

        # Check if the age graph exists
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT count(*) FROM ag_catalog.ag_graph WHERE name={graphName}").format(graphName=sql.Literal(GRAPH_NAME)))
            if cursor.fetchone()[0] == 0:
                raise GraphNotFound(GRAPH_NAME)

        # Get all vertices from the age graph
            cursor.execute("""SELECT * FROM cypher(%s, $$ MATCH (n) RETURN (n) $$) as (v agtype);""", (GRAPH_NAME,))
            for row in cursor:
                # Loading the nodes into the NetworkX graph
                G.add_node(row[0].id , label=row[0].label, properties=row[0].properties)

        # Get all edges from the age graph
            cursor.execute("""SELECT * FROM cypher(%s, $$ MATCH ()-[r]-() RETURN (r) $$) as (e agtype);""", (GRAPH_NAME,))
            # cursor = ag.execCypher("MATCH ()-[r]-() RETURN (r)")
            for row in cursor:
                # Loading the edges into the NetworkX graph
                G.add_edge(row[0].start_id, row[0].end_id, label=row[0].label, properties=row[0].properties)

        conn.commit()

        # Drawing the NetworkX graph
        nx.draw(G, with_labels=True,  width=2, edge_color='grey')
        plt.show()

    except Exception as e:
        print(e)
        conn.rollback()





"""
    Load PATH retrieved as cypher query output into a NetworkX DiGraph object and visualize them
    This function first checks if the given AGE graph exists in the database.
    If it does, it retrieves all paths (consisting of vertices and edges) from the graph,
    and creates a NetworkX DiGraph object with the same structure.
"""

def load_agePath_to_network():
    try: 

        # Creating a NetworkX graph
        G = nx.DiGraph() 

        # Check if the age graph exists
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT count(*) FROM ag_catalog.ag_graph WHERE name={graphName}").format(graphName=sql.Literal(GRAPH_NAME)))
            if cursor.fetchone()[0] == 0:
                raise GraphNotFound(GRAPH_NAME)
            
    # NOTE: This query is just for testing purposes , it will be replaced by the user's query
            cursor.execute("""SELECT * FROM cypher(%s, $$ MATCH p=()-[]-()
                RETURN p $$) as (e agtype);""", (GRAPH_NAME,))
            
            
            for row in cursor:
                path = row[0]

                #Verifying that Output is a path 
                if path.gtype == age.TP_PATH:
                    for e in path:

                        #Loading the vertices into the NetworkX graph
                        if e.gtype == age.TP_VERTEX:
                            G.add_node(e.id , label=e.label, properties=e.properties)
                        #Loading the edges into the NetworkX graph
                        elif e.gtype == age.TP_EDGE:
                            G.add_edge(e.start_id, e.end_id, label=e.label, properties=e.properties)
                    # If Cypher Output is not a Graph , Raise Exception
                else: 
                    raise Exception("Cypher Output is not a PATH!")
                    conn.rollback()

                # Commiting changes         
                conn.commit()
        
                    # Drawing the NetworkX graph       
        nx.draw(G, with_labels=True,  width=2, edge_color='grey')
        plt.show()

                
    except Exception as e:
        print(e)
        conn.rollback()



#Main
if __name__ == "__main__":

    load_graph_to_networkx()
    # load_agePath_to_network()
