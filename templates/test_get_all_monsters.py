from neo4j import GraphDatabase
import time

# Neo4j connection details
uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))


# Function to run the query and measure execution time
def test_query_execution_time():
    driver = GraphDatabase.driver(uri, auth=(user, password))

    query = """
    MATCH (m:Monster {name: 'Jim Darkmagic'})
    OPTIONAL MATCH (m)-[:HAS_SIZE]->(size:Size)
    OPTIONAL MATCH (m)-[:HAS_TYPE]->(type:Type)
    OPTIONAL MATCH (m)-[:HAS_ALIGNMENT]->(alignment:Alignment)
    OPTIONAL MATCH (m)-[:HAS_CR]->(cr:ChallengeRating)
    OPTIONAL MATCH (m)-[:HAS_SPEED]->(speed:Speed)
    OPTIONAL MATCH (m)-[:KNOWS_LANGUAGE]->(language:Language)
    OPTIONAL MATCH (m)-[:HAS_TRAIT]->(trait:Trait)
    OPTIONAL MATCH (m)-[:HAS_ACTION]->(action:Action)
    OPTIONAL MATCH (m)-[:HAS_AC]->(ac:ArmorClass)
    OPTIONAL MATCH (m)-[:HAS_TAG]->(tag:Tag)
    OPTIONAL MATCH (m)-[:HAS_SKILL]->(skill:Skill)
    OPTIONAL MATCH (m)-[:HAS_SAVE]->(save:Save)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_0]->(spell0:Spell)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_1]->(spell1:Spell)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_2]->(spell2:Spell)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_3]->(spell3:Spell)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_4]->(spell4:Spell)
    OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_5]->(spell5:Spell)
    RETURN m, size, type, alignment, cr, speed, language, trait, action, ac, tag, skill, save, 
           collect(spell0) as spell0, collect(spell1) as spell1, 
           collect(spell2) as spell2, collect(spell3) as spell3, 
           collect(spell4) as spell4, collect(spell5) as spell5
    """

    with driver.session() as session:
        start_time = time.time()
        result = session.run(query)
        end_time = time.time()

        for record in result:
            print(record)

        print(f"Query execution time: {end_time - start_time} seconds")

    driver.close()

# Run the function
test_query_execution_time()
