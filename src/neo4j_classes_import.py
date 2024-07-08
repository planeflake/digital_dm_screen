from neo4j import GraphDatabase
import neo4j.exceptions
import json
import glob
import os

uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))

from neo4j import GraphDatabase
import json
import os

# Establish connection to the Neo4j database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"  # Change this to your actual password

driver = GraphDatabase.driver(uri, auth=(username, password))

def create_or_update_class(tx, class_name, class_source):
    query = """
    MERGE (c:Class {name: $class_name})
    ON CREATE SET c.source = $class_source
    ON MATCH SET c.source = $class_source
    RETURN c
    """
    tx.run(query, class_name=class_name, class_source=class_source)

def create_or_update_source(tx, source_name, source_abbrev):
    query = """
    MERGE (s:Source {name: $source_name})
    ON CREATE SET s.abbrev = $source_abbrev
    ON MATCH SET s.abbrev = $source_abbrev
    RETURN s
    """
    tx.run(query, source_name=source_name, source_abbrev=source_abbrev)

def create_or_update_subclass(tx, subclass_name, subclass_source, class_name):
    query = """
    MERGE (sc:Subclass {name: $subclass_name, source: $subclass_source})
    WITH sc
    MATCH (c:Class {name: $class_name})
    MERGE (c)-[:HAS_SUBCLASS]->(sc)
    RETURN sc
    """
    tx.run(query, subclass_name=subclass_name, subclass_source=subclass_source, class_name=class_name)

def create_or_update_feature(tx, feature_name, feature_source, feature_level, parent_name, parent_label, relationship):
    query = f"""
    MERGE (f:Feature {{name: $feature_name, source: $feature_source, level: $feature_level}})
    WITH f
    MATCH (p:{parent_label} {{name: $parent_name}})
    MERGE (p)-[:{relationship}]->(f)
    RETURN f
    """
    tx.run(query, feature_name=feature_name, feature_source=feature_source, feature_level=feature_level, parent_name=parent_name)

def load_class_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if 'class' in data:
        for cls in data['class']:
            class_name = cls['name']
            class_source = cls['source']
            
            with driver.session() as session:
                session.write_transaction(create_or_update_class, class_name, class_source)
                
                for source in cls.get('otherSources', []):
                    session.write_transaction(create_or_update_source, source['source'], source['abbrev'])

                for feature in cls.get('classFeatures', []):
                    feature_name = feature['name']
                    feature_source = feature['source']
                    feature_level = feature['level']
                    session.write_transaction(create_or_update_feature, feature_name, feature_source, feature_level, class_name, 'Class', 'HAS_FEATURE')

        for subclass in data.get('subclass', []):
            subclass_name = subclass['name']
            subclass_source = subclass['source']
            
            with driver.session() as session:
                session.write_transaction(create_or_update_subclass, subclass_name, subclass_source, class_name)
                
                for feature in subclass.get('subclassFeatures', []):
                    feature_name = feature['name']
                    feature_source = feature['source']
                    feature_level = feature['level']
                    session.write_transaction(create_or_update_feature, feature_name, feature_source, feature_level, subclass_name, 'Subclass', 'HAS_FEATURE')

def load_all_class_data(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            print(f"Loading data from {file_path}")
            load_class_data(file_path)

# Load all class data from the specified directory
directory = "G:/5etools/data/class"
load_all_class_data(directory)
