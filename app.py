from flask import Flask, render_template, request, redirect, url_for
from neo4j import GraphDatabase

app = Flask(__name__)

# Neo4j connection
uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))

# Dummy player data
players = [
    {'username': 'player1'},
    {'username': 'player2'},
    {'username': 'dm'}  # Adding the dm user here
]

# Jinja2 filter for calculating ability modifiers
@app.template_filter('modifier')
def modifier_filter(score):
    return (score - 10) // 2

app.jinja_env.filters['modifier'] = modifier_filter


def get_characters_for_player(username):
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Player {username: $username})-[:HAS_CHARACTER]->(c:Character) "
            "RETURN c.name AS name, id(c) AS id", username=username)
        characters = [{"name": record["name"], "id": record["id"]} for record in result]
        print('Characters for player: ' + str(characters) + ' ' + str(username) + ' ' + str(result))
    return characters

def get_character_details(character_id):
    with driver.session() as session:
        print('Fetching character details for: ' + str(character_id) + ' ' + str(session))
        result = session.run(
            """
            MATCH (c:Character)-[:BELONGS_TO_CLASS]->(cl:Class),
                  (c)-[:BELONGS_TO_RACE]->(r:Races)
            WHERE id(c) = $character_id
            RETURN c.name AS name, c.level AS level, c.strength AS strength, 
                   c.dexterity AS dexterity, c.constitution AS constitution, 
                   c.intelligence AS intelligence, c.wisdom AS wisdom, 
                   c.charisma AS charisma, c.hit_points AS hit_points, 
                   c.armor_class AS armor_class, c.speed AS speed, 
                   c.alignment AS alignment, c.background AS background, 
                   cl.name AS class, r.name AS race
            """, character_id=character_id)
        return result.single()

def get_classes():
    with driver.session() as session:
        result = session.run("MATCH (c:Class) RETURN c.name AS name")
        classes = [record["name"] for record in result]
    return classes

def get_races():
    with driver.session() as session:
        result = session.run("MATCH (r:Race) RETURN r.name AS name")
        races = [record["name"] for record in result]
    return races

def get_alignments():
    # Assuming alignments are stored as a list in the code
    return ['Lawful Good', 'Neutral Good', 'Chaotic Good', 'Lawful Neutral', 'True Neutral', 'Chaotic Neutral', 'Lawful Evil', 'Neutral Evil', 'Chaotic Evil']

def get_backgrounds():
    # Assuming backgrounds are stored as a list in the code
    return ['Acolyte', 'Charlatan', 'Criminal', 'Entertainer', 'Folk Hero', 'Guild Artisan', 'Hermit', 'Noble', 'Outlander', 'Sage', 'Sailor', 'Soldier', 'Urchin']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/players/<username>')
def players_main(username):
    characters = get_characters_for_player(username)
    return render_template('players_main.html', username=username, characters=characters)

@app.route('/load_character/<int:character_id>', methods=['POST'])
def load_character(character_id):
    return redirect(url_for('character_dashboard', character_id=character_id))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if username == 'dm':
        return redirect(url_for('dm_dashboard', username=username))
    elif any(player['username'] == username for player in players):
        return redirect(url_for('player_dashboard', username=username))
    return redirect(url_for('home'))

@app.route('/player_dashboard/<username>', methods=['GET', 'POST'])
def player_dashboard(username):
    player_data = next((player for player in players if player['username'] == username), None)
    if not player_data:
        return redirect(url_for('home'))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Player {username: $username})-[:HAS_CHARACTER]->(char:Character)-[:BELONGS_TO_CLASS]->(cl:Class)
            RETURN char.name AS name, char.level AS level, cl.name AS class, id(char) as id,
                   char.strength AS strength, char.dexterity AS dexterity,
                   char.constitution AS constitution, char.intelligence AS intelligence,
                   char.wisdom AS wisdom, char.charisma AS charisma
            """,
            username=username
        )
        characters = [{"name": record["name"], "class": record["class"], "level": record["level"],
                       "strength": record["strength"], "dexterity": record["dexterity"], 
                       "constitution": record["constitution"], "intelligence": record["intelligence"], 
                       "wisdom": record["wisdom"], "charisma": record["charisma"],"id": record["id"]} 
                      for record in result]
    
    if request.method == 'POST':
        # Handle form submissions here
        pass

    return render_template('player_dashboard.html', player_data=player_data, characters=characters)

@app.route('/create_character', methods=['GET', 'POST'])
def create_character():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        char_class = request.form['class']
        char_race = request.form['race']
        level = int(request.form['level'])
        strength = int(request.form['strength'])
        dexterity = int(request.form['dexterity'])
        constitution = int(request.form['constitution'])
        intelligence = int(request.form['intelligence'])
        wisdom = int(request.form['wisdom'])
        charisma = int(request.form['charisma'])
        hit_points = int(request.form['hit_points'])
        armor_class = int(request.form['armor_class'])
        speed = int(request.form['speed'])
        alignment = request.form['alignment']
        background = request.form['background']

        with driver.session() as session:
            session.run(
                """
                MERGE (p:Player {username: $username})
                MATCH (cl:Class {name: $char_class})
                MATCH (r:Race {name: $char_race})
                CREATE (char:Character {
                    name: $name,
                    level: $level,
                    strength: $strength,
                    dexterity: $dexterity,
                    constitution: $constitution,
                    intelligence: $intelligence,
                    wisdom: $wisdom,
                    charisma: $charisma,
                    hit_points: $hit_points,
                    armor_class: $armor_class,
                    speed: $speed,
                    alignment: $alignment,
                    background: $background
                })
                CREATE (p)-[:HAS_CHARACTER]->(char)
                CREATE (char)-[:BELONGS_TO_CLASS]->(cl)
                CREATE (char)-[:BELONGS_TO_RACE]->(r)
                """,
                username=username, name=name, char_class=char_class, char_race=char_race,
                level=level, strength=strength, dexterity=dexterity, constitution=constitution,
                intelligence=intelligence, wisdom=wisdom, charisma=charisma, hit_points=hit_points,
                armor_class=armor_class, speed=speed, alignment=alignment, background=background
            )
        return redirect(url_for('players_main', username=username))
    else:
        classes = get_classes()
        races = get_races()
        alignments = get_alignments()
        backgrounds = get_backgrounds()
        return render_template('create_character.html', classes=classes, races=races, alignments=alignments, backgrounds=backgrounds)

@app.route('/dm_dashboard/<username>', methods=['GET', 'POST'])
def dm_dashboard(username):
    player_data = next((player for player in players if player['username'] == username), None)
    if not player_data:
        return redirect(url_for('home'))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Player)-[:HAS_CHARACTER]->(char:Character)-[:BELONGS_TO_CLASS]->(cl:Class)
            RETURN p.username AS username, char.name AS name, char.level AS level, cl.name AS class,
                   char.strength AS strength, char.dexterity AS dexterity,
                   char.constitution AS constitution, char.intelligence AS intelligence,
                   char.wisdom AS wisdom, char.charisma AS charisma
            """
        )
        players_characters = {}
        for record in result:
            username = record["username"]
            if username not in players_characters:
                players_characters[username] = []
            players_characters[username].append({
                "name": record["name"], "class": record["class"], "level": record["level"],
                "strength": record["strength"], "dexterity": record["dexterity"], 
                "constitution": record["constitution"], "intelligence": record["intelligence"], 
                "wisdom": record["wisdom"], "charisma": record["charisma"]
            })
    
    return render_template('dm_dashboard.html', player_data=player_data, players_characters=players_characters)

@app.route('/spells', methods=['POST'])
def spells():
    school = request.form.get('school')
    spell_name = request.form.get('name')
    spells = []

    query = "MATCH (s:Spell)"
    conditions = []
    params = {}

    if school:
        conditions.append("()-[:BELONGS_TO]->(school:School {name: $school})")
        params['school'] = school

    if spell_name:
        conditions.append("s.name CONTAINS $spell_name")
        params['spell_name'] = spell_name

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " RETURN s.name AS name, s.level AS level, school.name AS school"

    with driver.session() as session:
        result = session.run(query, params)
        spells = [{"name": record["name"], "level": record["level"], "school": record["school"]} for record in result]

    return render_template('spells.html', spells=spells)

@app.route('/spells/<spell_name>')
def show_spell(spell_name):
    spell_details = {}
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (s:Spell {name: $spell_name})
            OPTIONAL MATCH (s)-[:BELONGS_TO]->(school:School)
            OPTIONAL MATCH (s)-[:CASTING_TIME]->(ct:CastingTime)
            OPTIONAL MATCH (s)-[:FROM_SOURCE]->(src:Source)
            OPTIONAL MATCH (s)-[:HAS_AREA_TAG]->(area:AreaTag)
            OPTIONAL MATCH (s)-[:HAS_COMPONENT]->(comp:Component)
            OPTIONAL MATCH (s)-[:HAS_ENTRY]->(entry:Entry)
            OPTIONAL MATCH (s)-[:HAS_MISC_TAG]->(misc:MiscTag)
            OPTIONAL MATCH (s)-[:HAS_RANGE]->(range:Range)
            OPTIONAL MATCH (s)-[:INFLECTS_CONDITION]->(cond:Condition)
            RETURN s.name AS name, s.level AS level, school.name AS school,
                   ct.time AS casting_time, src.name AS source,
                   area.tag AS area, COLLECT(DISTINCT comp.name) AS components,
                   entry.text AS entry, misc.tag AS misc_tag,
                   range.distance AS range, cond.name AS condition
            """,
            spell_name=spell_name
        )
        
        record = result.single()
        if record:
            spell_details = {
                "name": record["name"],
                "level": record["level"],
                "school": record["school"],
                "casting_time": record["casting_time"],
                "source": record["source"],
                "area": record["area"],
                "components": record["components"],
                "entry": record["entry"],
                "misc_tag": record["misc_tag"],
                "range": record["range"],
                "condition": record["condition"]
            }
    
    return render_template('show_spell.html', spell=spell_details)

def get_available_classes_and_races():
    with driver.session() as session:
        classes_result = session.run("MATCH (c:Class) RETURN c.name AS name")
        races_result = session.run("MATCH (r:Races) RETURN r.name AS name")
        
        classes = [record["name"] for record in classes_result]
        races = [record["name"] for record in races_result]
        print('Fetching Classes and Races: ' + str(classes) + ' ' + str(races))
    return classes, races

@app.route('/character_dashboard/<int:character_id>')
def character_dashboard(character_id):
    print('Requesting ' + str(character_id))
    character = get_character_details(character_id)
    print('Response for: ' + str(character_id) + ' ' + str(character))
    skills = calculate_skills(character)
    return render_template('character_dashboard.html', character=character, skills=skills)

def calculate_skills(character):
    proficiency_bonus = 2 + (character['level'] - 1) // 4  # assuming proficiency bonus increases at level 5, 9, 13, and 17
    skills = {
        'Acrobatics': character['dexterity'] + proficiency_bonus,
        'Animal Handling': character['wisdom'] + proficiency_bonus,
        'Arcana': character['intelligence'] + proficiency_bonus,
        'Athletics': character['strength'] + proficiency_bonus,
        'Deception': character['charisma'] + proficiency_bonus,
        'History': character['intelligence'] + proficiency_bonus,
        'Insight': character['wisdom'] + proficiency_bonus,
        'Intimidation': character['charisma'] + proficiency_bonus,
        'Investigation': character['intelligence'] + proficiency_bonus,
        'Medicine': character['wisdom'] + proficiency_bonus,
        'Nature': character['intelligence'] + proficiency_bonus,
        'Perception': character['wisdom'] + proficiency_bonus,
        'Performance': character['charisma'] + proficiency_bonus,
        'Persuasion': character['charisma'] + proficiency_bonus,
        'Religion': character['intelligence'] + proficiency_bonus,
        'Sleight of Hand': character['dexterity'] + proficiency_bonus,
        'Stealth': character['dexterity'] + proficiency_bonus,
        'Survival': character['wisdom'] + proficiency_bonus
    }
    return skills

if __name__ == '__main__':
    app.run(debug=True)
