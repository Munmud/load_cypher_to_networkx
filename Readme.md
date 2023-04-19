# Load AGE cypher query into networkx

## Installation
- Clone the github repo
- Go to project directory
- Install dependency : `pip install -r requirements.txt`
- Change connection string according to your age configuration from main.py
```py
conn = psycopg2.connect(
    host="localhost", 
    port="5430", 
    dbname="postgresDB", 
    user="postgresUser", 
    password="postgresPW")
```
- Run program : `python main.py`

## Used Cypher query to create nodes
```sql
SELECT * from cypher(
    'karate', 
    $$ 
        CREATE (v:People {'name' : 1}) 
        RETURN v
    $$
) as (v agtype); 
```

## Used Cypher query to create edges
```sql
SELECT * from cypher(
    'karate', 
    $$ 
        MATCH ( a:People {'name' : 1}), (b:People {'name' : 2}) 
        CREATE (a)-[r:WorkWith {}]->(b)
    $$) as (v agtype); 
```

## Used Cypher query to get all edges
```sql
SELECT * from cypher(
    'karate', 
    $$ 
        MATCH v=()-[]->() 
        RETURN v 
    $$
) as (v agtype); 
```