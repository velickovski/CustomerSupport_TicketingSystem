import sqlite3
import random

# Connect to the SQLite database
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

# List of random names
names = [
    "John Doe", "Jane Smith", "Alice Johnson", "Michael Brown", "Emily Davis",
    "David Wilson", "Sophia Garcia", "Liam Martinez", "Olivia Anderson", "Noah Taylor",
    "Mia Thomas", "James White", "Emma Lee", "Benjamin Harris", "Isabella Walker",
    "Lucas Hall", "Charlotte Allen", "Mason Young", "Amelia King", "Ethan Wright"
]

# List of product descriptions
products = [
    "Gold ring with diamond", "Silver necklace with emerald", "Platinum bracelet with sapphires",
    "Rose gold pendant with ruby", "White gold earrings with pearls", "Diamond-encrusted watch",
    "Emerald engagement ring", "Sapphire-studded brooch", "Ruby and diamond cufflinks",
    "Gold charm bracelet", "Silver anklet with charms", "Platinum wedding band",
    "Opal pendant necklace", "Amethyst ring", "Turquoise beaded necklace",
    "Topaz stud earrings", "Onyx cufflinks", "Pearl drop earrings",
    "Aquamarine ring", "Garnet bracelet"
]

# Insert the names and product descriptions into the 'products' table
for i in range(1,21):
    name = random.choice(names)
    product_description = products[i-1]  # Use each product description in order
    cursor.execute('''
        INSERT INTO users (name, product_description)
        VALUES (?, ?)
    ''', (name, product_description))

# Commit the changes and close the connection
conn.commit()
conn.close()
