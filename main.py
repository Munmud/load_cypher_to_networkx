import psycopg2
import age
import networkx as nx


# # set DB path and graph path
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")

GRAPH_NAME = "karate"

# python dictionary to string
def dictToStr( property):
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

def extract_vertices( vertices):
    """returns from an agtype to python dict vertices"""
    tmp = {}
    tmp['label'] = vertices.label
    tmp['id'] = vertices.id
    for x in vertices.properties:
        tmp[x] = vertices[x]
    return tmp

def extract_edge( edge):
    """returns from an agtype to python dict edge"""
    tmp = {}
    tmp['label'] = edge.label
    tmp['id'] = edge.id
    tmp['start_id'] = edge.start_id
    tmp['end_id'] = edge.end_id
    for x in edge.properties:
        tmp[x] = edge[x]
    return tmp

# Creating a new graph (Ignore for now)
def create_graph(nodes,edges):

    # Making sure a new graph created
    age.setUpAge(conn, GRAPH_NAME)
    age.deleteGraph(conn, GRAPH_NAME)
    age.setUpAge(conn, GRAPH_NAME)


    def set_vertices(label, property):
        """Add a vertices to the graph"""
        with conn.cursor() as cursor:

            query = """
            SELECT * from cypher(
                '%s', 
                $$ 
                    CREATE (v:%s %s) 
                    RETURN v
                $$
            ) as (v agtype); 
            """ % (GRAPH_NAME, label,dictToStr(property))
            # print(query)
            try :
                cursor.execute(query)
                conn.commit()
                for row in cursor:
                    return extract_vertices(row[0])
                        
                # When data inserted or updated, You must commit.
            except Exception as ex:
                print(type(ex), ex)
                # if exception occurs, you must rollback all transaction. 
                conn.rollback()

    def set_edge(label1, prop1, label2, prop2, edge_label, edge_prop):
        with conn.cursor() as cursor:
            query ="""
            SELECT * from cypher(
                '%s', 
                $$ 
                    MATCH ( a:%s %s), (b:%s %s) 
                    CREATE (a)-[r:%s %s]->(b)
                $$) as (v agtype); 
            """ % (
                GRAPH_NAME,label1,
                dictToStr(prop1), 
                label2, 
                dictToStr(prop2), 
                edge_label, 
                dictToStr(edge_prop)
            )
            try :
                cursor.execute(query)
                conn.commit()
                for row in cursor:
                    print(row[0])
                    return extract_edge(row[0])
            except Exception as ex:
                print(type(ex), ex)
                conn.rollback()

    for n in nodes:
        v = set_vertices(
            label="People",
            property=
            {
                'name' : n
            }
        )
        # print(v)

    for e in edges:
        # addEdge(e[0], e[1])
        edge = set_edge(
            label1='People',
            label2='People',
            prop1={
                'name' : e[0]
            }, 
            prop2={
                'name' : e[1]
            },
            edge_label='WorkWith',
            edge_prop={}
        )

# load cypher query in Networkx
def get_edgeList_from_cypherquery():
    with conn.cursor() as cursor:
        query = """
                SELECT * from cypher(
                    '%s', 
                    $$ 
                        MATCH v=()-[]->() 
                        RETURN v 
                    $$
                ) as (v agtype); 
                """ % (GRAPH_NAME)
        # print(query)
        edgeList=[]
        try :
            cursor.execute(query)
            conn.commit()
            for row in cursor:
                path = row[0]
                tmp = {}
                tmp['v1'] = extract_vertices(path[0])
                tmp['e'] = extract_edge(path[1])
                tmp['v2'] = extract_vertices(path[2])

                # print(tmp['v1']['name'], tmp['v2']['name'])
                edgeList.append([tmp['v1']['name'], tmp['v2']['name']])
                    
            # When data inserted or updated, You must commit.
            return edgeList
        except Exception as ex:
            print(type(ex), ex)
            # if exception occurs, you must rollback all transaction. 
            conn.rollback()


# Zachary's karate club
nodes = [p+1 for p in range(34)]
edges = [[2,1],[3,1],[3,2],[4,1],[4,2],[4,3],[5,1],[6,1],[7,1],[7,5],[7,6],[8,1],[8,2],[8,3],[8,4],[9,1],[9,3],[10,3],[11,1],[11,5],[11,6],[12,1],[13,1],[13,4],[14,1],[14,2],[14,3],[14,4],[17,6],[17,7],[18,1],[18,2],[20,1],[20,2],[22,1],[22,2],[26,24],[26,25],[28,3],[28,24],[28,25],[29,3],[30,24],[30,27],[31,2],[31,9],[32,1],[32,25],[32,26],[32,29],[33,3],[33,9],[33,15],[33,16],[33,19],[33,21],[33,23],[33,24],[33,30],[33,31],[33,32],[34,9],[34,10],[34,14],[34,15],[34,16],[34,19],[34,20],[34,21],[34,23],[34,24],[34,27],[34,28],[34,29],[34,30],[34,31],[34,32],[34,33]]

create_graph(nodes, edges)
edgeList = get_edgeList_from_cypherquery()
G=nx.from_edgelist(edgeList)

print("Number of nodes : " , G.number_of_nodes())
print("Number of edges : " , G.number_of_edges())

