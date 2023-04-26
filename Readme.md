# Python Support for Networkx
NetworkX is one of the well known python libraries to perform network analysis. Extracting a graph or subgraph from AGE and creating a NetworkX graph, performing operations on the graph and saving the resultant graph into AGE will allow developers and data scientists using NetworkX to use AGE.

Note : AGE support only Directed edge, We have converted age to Networkx Directed Graph and vice versa. For more information about [Networkx Directed Graph](https://networkx.org/documentation/stable/reference/classes/digraph.html)


## Load From AGE to Networkx
- This Function will load all the nodes and edges found from the graph into Networkx directed Graph
- View `sample_ageToNetworkx.py` file for sample use
```py
import psycopg2
from age_networkx import *

# Change the following connection according to your configuration
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")
GRAPH_NAME = 'karate'

G = ageToNetworkx(connection=conn, GRAPH_NAME= GRAPH_NAME)
```

## Load From Networkx to AGE
- This Function will add all the nodes and edges found from a Networkx Directed Graph to Apache AGE Graph Database.
- Here Id will be changed as AGE driver assign id for nodes and edges automatically
- View `sample_networkxToAge.py` file for sample use
```py
import psycopg2
from age_networkx import *
import networkx as nx

# Change the following connection according to your configuration
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")
GRAPH_NAME = 'karate'

G = nx.DiGraph()
# add nodes and edges here. 

networkxToAge(conn, G, GRAPH_NAME=GRAPH_NAME)
```