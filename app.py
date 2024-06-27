from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
from neo4j import GraphDatabase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Neo4j connection
uri = 'neo4j+s://b29956d6.databases.neo4j.io'
user = 'neo4j'
password = '0kc1APDksb8vIkSWOraGix4fulXDzr6d_81Uw5JLDbs'
driver = GraphDatabase.driver(uri, auth=(user, password))

# Dummy player data
players_list = [
    {'username': 'player1'},
    {'username': 'player2'},
    {'username': 'dm'}
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
    return characters

def get_conditions():
    with driver.session() as session:
        result = session.run("MATCH (c:Condition) RETURN c.name AS name, c.icon AS icon")
        conditions = [{"name": record["name"], "icon": record["icon"]} for record in result]
    return conditions

def get_characters_for_testing():
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Character)-[:BELONGS_TO_CLASS]->(cl:Class),
                  (c)-[:BELONGS_TO_RACE]->(r:Races)
            OPTIONAL MATCH (c)-[:HAS_AC]->(ac:ArmorClass)
            OPTIONAL MATCH (c)-[:HAS_CR]->(cr:ChallengeRating)
            OPTIONAL MATCH (c)-[:HAS_TYPE]->(type:Type)
            RETURN c.name AS characterName, id(c) AS characterId, cl.name AS className, r.name AS raceName,
                   c.level AS level, c.strength AS strength, c.dexterity AS dexterity, 
                   c.constitution AS constitution, c.intelligence AS intelligence,
                   c.wisdom AS wisdom, c.charisma AS charisma, c.token_url AS tokenUrl, 
                   ac.ac AS ac, cr.cr AS cr, type.type AS type
            """
        )
        characters = []
        for record in result:
            characters.append({
                "name": record["characterName"],
                "id": record["characterId"],
                "class": record["className"],
                "race": record["raceName"],
                "level": record["level"],
                "strength": record["strength"],
                "dexterity": record["dexterity"],
                "constitution": record["constitution"],
                "intelligence": record["intelligence"],
                "wisdom": record["wisdom"],
                "charisma": record["charisma"],
                "tokenUrl": record["tokenUrl"],
                "ac": record["ac"],
                "cr": record["cr"],
                "type": record["type"]
            })
        return characters

def get_character_details(character_id):
    with driver.session() as session:
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
    return ['Lawful Good', 'Neutral Good', 'Chaotic Good', 'Lawful Neutral', 'True Neutral', 'Chaotic Neutral', 'Lawful Evil', 'Neutral Evil', 'Chaotic Evil']

def get_backgrounds():
    return ['Acolyte', 'Charlatan', 'Criminal', 'Entertainer', 'Folk Hero', 'Guild Artisan', 'Hermit', 'Noble', 'Outlander', 'Sage', 'Sailor', 'Soldier', 'Urchin']

def get_five_monsters():
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
    if any(player['username'] == username for player in players_list):
        if username == 'dm':
            return redirect(url_for('dm_dashboard', username=username))
        return redirect(url_for('player_dashboard', username=username))
    return redirect(url_for('home'))

@app.route('/player_dashboard/<username>', methods=['GET', 'POST'])
def player_dashboard(username):
    player_data = next((player for player in players_list if player['username'] == username), None)
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
    monsters = get_five_monsters()
    characters = get_characters_for_testing()
    conditions=get_conditions()
    return render_template('dm_dashboard.html', monsters=monsters, characters=characters,conditions=conditions)

@app.route('/character_dashboard/<int:character_id>')
def character_dashboard(character_id):
    character = get_character_details(character_id)
    skills = calculate_skills(character)
    return render_template('character_dashboard.html', character=character, skills=skills)

def calculate_skills(character):
    return {
        'Acrobatics': character['dexterity'],
        'Animal Handling': character['wisdom'],
        'Arcana': character['intelligence'],
        'Athletics': character['strength'],
        'Deception': character['charisma'],
        'History': character['intelligence'],
        'Insight': character['wisdom'],
        'Intimidation': character['charisma'],
        'Investigation': character['intelligence'],
        'Medicine': character['wisdom'],
        'Nature': character['intelligence'],
        'Perception': character['wisdom'],
        'Performance': character['charisma'],
        'Persuasion': character['charisma'],
        'Religion': character['intelligence'],
        'Sleight of Hand': character['dexterity'],
        'Stealth': character['dexterity'],
        'Survival': character['wisdom'],
    }

@socketio.on('next_turn')
def handle_next_turn(data):
    socketio.emit('update_turn', data, broadcast=True)

@socketio.on('previous_turn')
def handle_previous_turn(data):
    socketio.emit('update_turn', data, broadcast=True)

@app.route('/api/players')
def get_players():
    with driver.session() as session:
        result = session.run("MATCH (p:Player)-[:HAS_CHARACTER]->(c:Character) RETURN p.username AS username, id(c) AS id, c.name AS name, c.hp AS hp, c.ac AS ac, c.spell AS spell")
        players = [{"username": record["username"], "id": record["id"], "name": record["name"], "hp": record["hp"], "ac": record["ac"], "spell": record["spell"]} for record in result]
    return jsonify(players)

@app.route('/api/monsters')
def get_monsters():
    with driver.session() as session:
        result = session.run("MATCH (m:Monster) RETURN m.name AS name, m.image AS image, m.hp AS hp, m.ac AS ac")
        monsters = [{"name": record["name"], "image": record["image"], "hp": record["hp"], "ac": record["ac"]} for record in result]
    return jsonify(monsters)

def get_all_players():
    with driver.session() as session:
        result = session.run("MATCH (p:Player) RETURN p.username AS username")
        players = [{"username": record["username"]} for record in result]
    return players

def get_all_monsters():
    with driver.session() as session:
        result = session.run("MATCH (m:Monster) RETURN m.name AS name, m.hp_average AS hp, m.dex AS dex, m.con AS con, m.int AS int, m.wis AS wis, m.cha AS cha, m.page AS page")
        monsters = [{"name": record["name"], "hp": record["hp"], "dex": record["dex"], "con": record["con"], "int": record["int"], "wis": record["wis"], "cha": record["cha"], "page": record["page"]} for record in result]
    return monsters

@app.route('/players')
def players():
    players = get_all_players()
    return jsonify(players)

@app.route('/monsters')
def monsters():
    monsters = get_all_monsters()
    return jsonify(monsters)

if __name__ == '__main__':
    socketio.run(app, debug=True)
