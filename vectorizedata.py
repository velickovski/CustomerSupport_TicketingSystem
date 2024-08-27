import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle

# Connect to SQLite
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Fetch data from the database
c.execute('SELECT id, description FROM products')
rows = c.fetchall()

descriptions = [row[1] for row in rows]

# Vectorize descriptions
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(descriptions)

# Convert sparse matrix to dense array
dense_array = tfidf_matrix.toarray()

# Add new column for vectorized data
for i, row in enumerate(rows):
    id = row[0]
    vector = dense_array[i]
    vector_blob = pickle.dumps(vector)  # Serialize the vector

    # Insert or update the vector in the database
    c.execute('''ALTER TABLE products ADD COLUMN vector BLOB''')
    c.execute('UPDATE products SET vector = ? WHERE id = ?', (vector_blob, id))

conn.commit()
conn.close()
