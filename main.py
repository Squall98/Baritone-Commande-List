import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget,
                             QPushButton, QComboBox, QTextBrowser)

def main():
    # Établissez une connexion à la base de données SQLite
    conn = sqlite3.connect('baritone_commands.db')

    # Créez la table de données si elle n'existe pas déjà
    conn.execute('''
        CREATE TABLE IF NOT EXISTS baritone_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            command TEXT,
            description TEXT
        )
    ''')

    # Vérifiez si la table est vide
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM baritone_commands')
    count = cursor.fetchone()[0]
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Documentation Baritone")
    window.setGeometry(100, 100, 800, 600)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    layout = QVBoxLayout()

    search_label = QLabel("Rechercher des commandes :")
    layout.addWidget(search_label)

    search_input = QLineEdit()
    layout.addWidget(search_input)

    search_button = QPushButton("Rechercher")
    layout.addWidget(search_button)

    category_label = QLabel("Sélectionner une catégorie :")
    layout.addWidget(category_label)

    category_combobox = QComboBox()
    # Fetch categories from the database and add them to the QComboBox
    cursor.execute("SELECT DISTINCT category FROM baritone_commands")
    categories = cursor.fetchall()
    category_combobox.addItem("Toutes les Catégories")
    for category in categories:
        category_combobox.addItem(category[0])
    layout.addWidget(category_combobox)

    commands_text = QTextBrowser()
    commands_text.setReadOnly(True)
    layout.addWidget(commands_text)

    central_widget.setLayout(layout)

    # Si la table est vide, affichez un message
    if count == 0:
        print("La base de données est vide. Ajoutez des données pour continuer.")

    def display_commands(category=None, search=None):
        query = 'SELECT command, description FROM baritone_commands'
        params = []

        conditions = []
        if category and category != "Toutes les Catégories":
            conditions.append('category = ?')
            params.append(category)

        if search:
            # Recherche à la fois dans les commandes et les descriptions
            conditions.append('(command LIKE ? OR description LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        cursor.execute(query, params)
        result = cursor.fetchall()

        commands_text.clear()
        for row in result:
            commands_text.append(f"Commande : {row[0]}\nDescription : {row[1]}\n")

    def on_search():
        search_term = search_input.text()
        display_commands(search=search_term)

    search_button.clicked.connect(on_search)
    category_combobox.currentIndexChanged.connect(lambda: display_commands(category=category_combobox.currentText()))

    def display_command_details():
        selected_text = commands_text.textCursor().selectedText()
        if selected_text:
            cursor.execute('''
                SELECT description
                FROM baritone_commands
                WHERE command = ?
            ''', (selected_text,))
            result = cursor.fetchone()
            if result:
                commands_text.clear()
                commands_text.append(f"Description : {result[0]}\n")

    commands_text.anchorClicked.connect(display_command_details)

    # Texte d'accueil initial
    commands_text.setPlainText("Bienvenue dans la Documentation Baritone!\nSélectionnez une catégorie ou recherchez pour voir les commandes.")

    window.show()
    sys.exit(app.exec_())
    conn.close()

if __name__ == "__main__":
    main()
