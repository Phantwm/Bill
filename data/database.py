import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

conn = sqlite3.connect('data/database.db')
conn.execute('CREATE TABLE IF NOT EXISTS trainers (gamemode TEXT, user_id INTEGER, message_id INTEGER, ign TEXT, price TEXT, colour INTEGER, description TEXT, active INTEGER, lessons INTEGER, PRIMARY KEY (gamemode, user_id))')
conn.execute('CREATE TABLE IF NOT EXISTS tickets (channel_id INTEGER PRIMARY KEY, trainer_id INTEGER, customer_id INTEGER, gamemode TEXT)')
try:
    conn.execute('ALTER TABLE tickets ADD COLUMN customer_id INTEGER')
    conn.execute('ALTER TABLE tickets ADD COLUMN gamemode TEXT')
except:
    pass
try:
    conn.execute('ALTER TABLE trainers ADD COLUMN active INTEGER')
except:
    pass
try:
    conn.execute('ALTER TABLE trainers ADD COLUMN lessons INTEGER')
except:
    pass
conn.commit()

def add_trainer(gamemode, user_id):
    defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`", 1, 0)
    conn.execute('INSERT OR IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description, active, lessons) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (gamemode, user_id, *defaults))
    conn.execute('UPDATE trainers SET ign = COALESCE(ign, ?), price = COALESCE(price, ?), colour = COALESCE(colour, ?), description = COALESCE(description, ?), active = COALESCE(active, ?), lessons = COALESCE(lessons, ?) WHERE gamemode = ? AND user_id = ?', (*defaults, gamemode, user_id))
    conn.commit()

def get_panel_message_id(gamemode, user_id):
    cursor = conn.execute('SELECT message_id FROM trainers WHERE gamemode = ? AND user_id = ?', (gamemode, user_id))
    row = cursor.fetchone()
    return row[0] if row else None

def get_trainer_by_message(message_id):
    cursor = conn.execute('SELECT user_id, gamemode FROM trainers WHERE message_id = ?', (message_id,))
    row = cursor.fetchone()
    return {"user_id": row[0], "gamemode": row[1]} if row else None

def set_panel_message_id(gamemode, user_id, message_id):
    conn.execute('INSERT OR REPLACE INTO trainers (gamemode, user_id, message_id) VALUES (?, ?, ?)', (gamemode, user_id, message_id))
    conn.commit()

def get_panel_data(gamemode, user_id):
    defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`", 1, 0)
    row = conn.execute('SELECT COALESCE(ign, ?), COALESCE(price, ?), COALESCE(colour, ?), COALESCE(description, ?), COALESCE(active, ?), COALESCE(lessons, ?) FROM trainers WHERE gamemode = ? AND user_id = ?', (*defaults, gamemode, user_id)).fetchone()
    return {"ign": row[0], "price": row[1], "colour": row[2], "description": row[3], "active": bool(row[4]), "lessons": row[5]}

_defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`")

def set_panel_ign(gamemode, user_id, ign):
    conn.execute('INSERT OR IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (?, ?, ?, ?, ?, ?)', (gamemode, user_id, *_defaults[:4]))
    conn.execute('UPDATE trainers SET ign = ?, price = COALESCE(price, ?), colour = COALESCE(colour, ?), description = COALESCE(description, ?) WHERE gamemode = ? AND user_id = ?', (ign, *_defaults[:4], gamemode, user_id))
    conn.commit()

def set_panel_price(gamemode, user_id, price):
    conn.execute('INSERT OR IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (?, ?, ?, ?, ?, ?)', (gamemode, user_id, *_defaults[:4]))
    conn.execute('UPDATE trainers SET ign = COALESCE(ign, ?), price = ?, colour = COALESCE(colour, ?), description = COALESCE(description, ?) WHERE gamemode = ? AND user_id = ?', (*_defaults[:3], price, _defaults[3], gamemode, user_id))
    conn.commit()

def set_panel_colour(gamemode, user_id, colour):
    conn.execute('INSERT OR IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (?, ?, ?, ?, ?, ?)', (gamemode, user_id, *_defaults[:4]))
    conn.execute('UPDATE trainers SET ign = COALESCE(ign, ?), price = COALESCE(price, ?), colour = ?, description = COALESCE(description, ?) WHERE gamemode = ? AND user_id = ?', (*_defaults[:2], colour, _defaults[3], gamemode, user_id))
    conn.commit()

def set_panel_description(gamemode, user_id, description):
    conn.execute('INSERT OR IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (?, ?, ?, ?, ?, ?)', (gamemode, user_id, *_defaults[:4]))
    conn.execute('UPDATE trainers SET ign = COALESCE(ign, ?), price = COALESCE(price, ?), colour = COALESCE(colour, ?), description = ? WHERE gamemode = ? AND user_id = ?', (*_defaults[:3], description, gamemode, user_id))
    conn.commit()

def add_ticket(channel_id, trainer_id, customer_id, gamemode):
    conn.execute('INSERT OR REPLACE INTO tickets (channel_id, trainer_id, customer_id, gamemode) VALUES (?, ?, ?, ?)', (channel_id, trainer_id, customer_id, gamemode))
    conn.commit()

def get_ticket_info(channel_id):
    cursor = conn.execute('SELECT trainer_id, customer_id, gamemode FROM tickets WHERE channel_id = ?', (channel_id,))
    row = cursor.fetchone()
    return {"trainer_id": row[0], "customer_id": row[1], "gamemode": row[2]} if row else None

def remove_ticket(channel_id):
    conn.execute('DELETE FROM tickets WHERE channel_id = ?', (channel_id,))
    conn.commit()

def get_trainer_ign(gamemode, trainer_id):
    cursor = conn.execute('SELECT ign FROM trainers WHERE gamemode = ? AND user_id = ?', (gamemode, trainer_id))
    row = cursor.fetchone()
    return row[0] if row else None

def toggle_active(gamemode, user_id):
    cursor = conn.execute('SELECT active FROM trainers WHERE gamemode = ? AND user_id = ?', (gamemode, user_id))
    row = cursor.fetchone()
    current_active = 1 if (row and row[0]) else 0
    new_active = 0 if current_active else 1
    conn.execute('UPDATE trainers SET active = ? WHERE gamemode = ? AND user_id = ?', (new_active, gamemode, user_id))
    conn.commit()
    return bool(new_active)

def increment_lessons(gamemode, user_id):
    conn.execute('UPDATE trainers SET lessons = COALESCE(lessons, 0) + 1 WHERE gamemode = ? AND user_id = ?', (gamemode, user_id))
    conn.commit()

