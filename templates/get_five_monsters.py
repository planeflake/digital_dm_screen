import logging
from neo4j import GraphDatabase

# Set up logging
logging.basicConfig(level=logging.WARNING)

# Neo4j connection details
uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_five_monsters():
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (m:Monster)
                OPTIONAL MATCH (m)-[:HAS_AC]->(ac:ArmorClass)
                OPTIONAL MATCH (m)-[:HAS_CR]->(cr:ChallengeRating)
                OPTIONAL MATCH (m)-[:HAS_TYPE]->(type:Type)
                RETURN m.name AS name, ac.ac AS ac, cr.cr AS cr, type.type AS type, m.token_url as tokenUrl
                LIMIT 5
                """
            )
            monsters = []
            for record in result:
                monsters.append({
                    "name": record["name"],
                    "ac": record["ac"],
                    "cr": record["cr"],
                    "type": record["type"],
                    "tokenUrl": record["tokenUrl"]
                })
            return monsters
    except Exception as e:
        logging.error("An error occurred: %s", str(e))

if __name__ == '__main__':
    monsters = get_five_monsters()
    for monster in monsters:
        print(monster)
