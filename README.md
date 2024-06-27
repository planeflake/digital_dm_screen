
# D&D Digital Player Screen

This project is a digital player screen for Dungeons & Dragons, allowing players to manage their characters and access game information in an interactive way. The application is built using Flask and Neo4j, providing a web-based interface for players and dungeon masters.

## Features

- **Character Management**: Create and manage D&D characters.
- **Spellbook**: Access and view spells available to characters.
- **Inventory Management**: Manage character inventory.
- **DM Dashboard**: A special dashboard for dungeon masters to manage the game.
- **Responsive Design**: Designed for use on tablets and other touch devices.

## Installation

### Prerequisites

- Python 3.7+
- Neo4j Database
- Flask
- Neo4j Python Driver

### Setup

1. **Clone the repository**:

    ```sh
    git clone https://github.com/planeflake/digital_dm_screen.git
    cd digital_dm_screen
    ```

2. **Create a virtual environment**:

    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment**:

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```sh
        source venv/bin/activate
        ```

4. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

5. **Setup Neo4j Database**:

    - Ensure you have a running instance of Neo4j.
    - Update the `uri`, `user`, and `password` variables in `app.py` to match your Neo4j instance.

6. **Run the application**:

    ```sh
    flask run
    ```

    The application will be available at `http://127.0.0.1:5000`.

## Usage

- **Home Page**: Choose to log in as a player or dungeon master.
- **Player Dashboard**: View and manage your characters.
- **DM Dashboard**: Manage the game as a dungeon master.
- **Character Dashboard**: View character details, spellbook, inventory, and more.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.
