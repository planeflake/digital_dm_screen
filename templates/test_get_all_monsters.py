from neo4j import GraphDatabase

# Neo4j connection details
uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_monster_details(name):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (m:Monster {name: $name})
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_0]->(spell0:Spell)
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_1]->(spell1:Spell)
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_2]->(spell2:Spell)
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_3]->(spell3:Spell)
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_4]->(spell4:Spell)
            OPTIONAL MATCH (m)-[:CAN_CAST_SPELL_LEVEL_5]->(spell5:Spell)
            OPTIONAL MATCH (m)-[:HAS_AC]->(ac:AC)
            OPTIONAL MATCH (m)-[:HAS_ACTION]->(act:Action)
            OPTIONAL MATCH (m)-[:HAS_ALIGNMENT]->(al:Alignment)
            OPTIONAL MATCH (m)-[:HAS_CR]->(cr:CR)
            OPTIONAL MATCH (m)-[:HAS_DAMAGE_TAG]->(damage:DamageTag)
            OPTIONAL MATCH (m)-[:HAS_LANGUAGE_TAG]->(lang_tag:LanguageTag)
            OPTIONAL MATCH (m)-[:HAS_MAIN_SOURCE]->(source:Source)
            OPTIONAL MATCH (m)-[:HAS_MISC_TAG]->(misc:MiscTag)
            OPTIONAL MATCH (m)-[:HAS_SAVE]->(save:Save)
            OPTIONAL MATCH (m)-[:HAS_SIZE]->(size:Size)
            OPTIONAL MATCH (m)-[:HAS_SKILL]->(skill:Skill)
            OPTIONAL MATCH (m)-[:HAS_SPEED]->(speed:Speed)
            OPTIONAL MATCH (m)-[:HAS_TAG]->(tag:Tag)
            OPTIONAL MATCH (m)-[:HAS_TRAIT]->(trait:Trait)
            OPTIONAL MATCH (m)-[:HAS_TYPE]->(type:Type)
            OPTIONAL MATCH (m)-[:KNOWS_LANGUAGE]->(lang:Language)
            RETURN m.name AS name, m.hp_average AS hp, m.dex AS dex, m.con AS con, m.int AS int, 
                   m.wis AS wis, m.cha AS cha, m.page AS page, 
                   COLLECT(DISTINCT spell0.name) AS spell_level_0, 
                   COLLECT(DISTINCT spell1.name) AS spell_level_1,
                   COLLECT(DISTINCT spell2.name) AS spell_level_2,
                   COLLECT(DISTINCT spell3.name) AS spell_level_3,
                   COLLECT(DISTINCT spell4.name) AS spell_level_4,
                   COLLECT(DISTINCT spell5.name) AS spell_level_5,
                   COLLECT(DISTINCT ac.value) AS ac_values,
                   COLLECT(DISTINCT act.name) AS actions,
                   COLLECT(DISTINCT al.name) AS alignments,
                   COLLECT(DISTINCT cr.value) AS cr_values,
                   COLLECT(DISTINCT damage.name) AS damage_tags,
                   COLLECT(DISTINCT lang_tag.name) AS language_tags,
                   COLLECT(DISTINCT source.name) AS sources,
                   COLLECT(DISTINCT misc.name) AS misc_tags,
                   COLLECT(DISTINCT save.name) AS saves,
                   COLLECT(DISTINCT size.value) AS sizes,
                   COLLECT(DISTINCT skill.name) AS skills,
                   COLLECT(DISTINCT speed.value) AS speeds,
                   COLLECT(DISTINCT tag.name) AS tags,
                   COLLECT(DISTINCT trait.name) AS traits,
                   COLLECT(DISTINCT type.name) AS types,
                   COLLECT(DISTINCT lang.name) AS languages
            """, name=name
        )
        monster = result.single()
        return {
            "name": monster["name"],
            "hp": monster["hp"],
            "dex": monster["dex"],
            "con": monster["con"],
            "int": monster["int"],
            "wis": monster["wis"],
            "cha": monster["cha"],
            "page": monster["page"],
            "spell_level_0": monster["spell_level_0"],
            "spell_level_1": monster["spell_level_1"],
            "spell_level_2": monster["spell_level_2"],
            "spell_level_3": monster["spell_level_3"],
            "spell_level_4": monster["spell_level_4"],
            "spell_level_5": monster["spell_level_5"],
            "ac_values": monster["ac_values"],
            "actions": monster["actions"],
            "alignments": monster["alignments"],
            "cr_values": monster["cr_values"],
            "damage_tags": monster["damage_tags"],
            "language_tags": monster["language_tags"],
            "sources": monster["sources"],
            "misc_tags": monster["misc_tags"],
            "saves": monster["saves"],
            "sizes": monster["sizes"],
            "skills": monster["skills"],
            "speeds": monster["speeds"],
            "tags": monster["tags"],
            "traits": monster["traits"],
            "types": monster["types"],
            "languages": monster["languages"]
        }

if __name__ == '__main__':
    monster_details = get_monster_details("Jim Darkmagic")
    print(monster_details)
