"""
Author : Moontasir Mahmood
Githut : munmud
"""
import psycopg2
from age_networkx import *

# set DB path and graph name
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")
GRAPH_NAME = 'karate'

G = ageToNetworkx(connection=conn, GRAPH_NAME= GRAPH_NAME)

for u, v in G.edges:
    print(f"Edge \n ({G.nodes[u]}, \n {G.nodes[v]}) \n with label : {G.edges[u, v]['label']}  \n has properties : {G.edges[u, v]['properties']}")

print(G)
