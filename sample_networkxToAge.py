"""
Author : Moontasir Mahmood
Github : munmud
"""

import psycopg2
from age_networkx import *
import networkx as nx

# set DB path and graph name
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")
GRAPH_NAME = 'karate'

# Create an empty directed graph
G = nx.DiGraph()

# Add nodes with properties
G.add_node('1', 
           label='People',
           properties={'name' : 'Moontasir',
                       'weight' : '50kg'})
G.add_node('2', 
           label='People', 
           properties={'name': 'Shoaib' ,
                       'weight' : '60kg'})

# Add edges with properties
G.add_edge('1', '2', label='ProjectLeader', properties={'firstMeet' : 'Jan-21-2019'} )

networkxToAge(conn, G, GRAPH_NAME=GRAPH_NAME)
