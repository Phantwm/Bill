import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def get_conn():
    mysql_url = os.getenv('MYSQL_URL') or os.getenv('MYSQL_PUBLIC_URL')
    if mysql_url:
        parsed = urlparse(mysql_url)
        return pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            charset='utf8mb4'
        )
    return pymysql.connect(
        host=os.getenv('MYSQLHOST'),
        port=int(os.getenv('MYSQLPORT', 3306)),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE'),
        charset='utf8mb4'
    )

conn = get_conn()
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS trainers (gamemode VARCHAR(255), user_id BIGINT, message_id BIGINT, ign VARCHAR(255), price VARCHAR(255), colour INT, description TEXT, active TINYINT, lessons INT, PRIMARY KEY (gamemode, user_id))')
cursor.execute('CREATE TABLE IF NOT EXISTS tickets (channel_id BIGINT PRIMARY KEY, trainer_id BIGINT, customer_id BIGINT, gamemode VARCHAR(255))')
try:
    cursor.execute('ALTER TABLE tickets ADD COLUMN customer_id BIGINT')
except:
    pass
try:
    cursor.execute('ALTER TABLE tickets ADD COLUMN gamemode VARCHAR(255)')
except:
    pass
try:
    cursor.execute('ALTER TABLE trainers ADD COLUMN active TINYINT')
except:
    pass
try:
    cursor.execute('ALTER TABLE trainers ADD COLUMN lessons INT')
except:
    pass
conn.commit()

def add_trainer(gamemode, user_id):
    defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`", 1, 0)
    cursor = conn.cursor()
    cursor.execute('INSERT IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description, active, lessons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (gamemode, user_id, *defaults))
    cursor.execute('UPDATE trainers SET ign = COALESCE(ign, %s), price = COALESCE(price, %s), colour = COALESCE(colour, %s), description = COALESCE(description, %s), active = COALESCE(active, %s), lessons = COALESCE(lessons, %s) WHERE gamemode = %s AND user_id = %s', (*defaults, gamemode, user_id))
    conn.commit()

def get_panel_message_id(gamemode, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT message_id FROM trainers WHERE gamemode = %s AND user_id = %s', (gamemode, user_id))
    row = cursor.fetchone()
    return row[0] if row else None

def get_trainer_by_message(message_id):
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, gamemode FROM trainers WHERE message_id = %s', (message_id,))
    row = cursor.fetchone()
    return {"user_id": row[0], "gamemode": row[1]} if row else None

def set_panel_message_id(gamemode, user_id, message_id):
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO trainers (gamemode, user_id, message_id) VALUES (%s, %s, %s)', (gamemode, user_id, message_id))
    conn.commit()

def get_panel_data(gamemode, user_id):
    defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`", 1, 0)
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(ign, %s), COALESCE(price, %s), COALESCE(colour, %s), COALESCE(description, %s), COALESCE(active, %s), COALESCE(lessons, %s) FROM trainers WHERE gamemode = %s AND user_id = %s', (*defaults, gamemode, user_id))
    row = cursor.fetchone()
    return {"ign": row[0], "price": row[1], "colour": row[2], "description": row[3], "active": bool(row[4]), "lessons": row[5]}

_defaults = ("Example", "10", 3092790, "# **This** __is__ *an* ~~example~~ `description`\n\n## **This** __is__ *an* ~~example~~ `description`\n\n### **This** __is__ *an* ~~example~~ `description`\n\n**This** __is__ *an* ~~example~~ `description`\n\n-# **This** __is__ *an* ~~example~~ `description`")

def set_panel_ign(gamemode, user_id, ign):
    cursor = conn.cursor()
    cursor.execute('INSERT IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (%s, %s, %s, %s, %s, %s)', (gamemode, user_id, *_defaults[:4]))
    cursor.execute('UPDATE trainers SET ign = %s, price = COALESCE(price, %s), colour = COALESCE(colour, %s), description = COALESCE(description, %s) WHERE gamemode = %s AND user_id = %s', (ign, *_defaults[:4], gamemode, user_id))
    conn.commit()

def set_panel_price(gamemode, user_id, price):
    cursor = conn.cursor()
    cursor.execute('INSERT IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (%s, %s, %s, %s, %s, %s)', (gamemode, user_id, *_defaults[:4]))
    cursor.execute('UPDATE trainers SET ign = COALESCE(ign, %s), price = %s, colour = COALESCE(colour, %s), description = COALESCE(description, %s) WHERE gamemode = %s AND user_id = %s', (*_defaults[:3], price, _defaults[3], gamemode, user_id))
    conn.commit()

def set_panel_colour(gamemode, user_id, colour):
    cursor = conn.cursor()
    cursor.execute('INSERT IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (%s, %s, %s, %s, %s, %s)', (gamemode, user_id, *_defaults[:4]))
    cursor.execute('UPDATE trainers SET ign = COALESCE(ign, %s), price = COALESCE(price, %s), colour = %s, description = COALESCE(description, %s) WHERE gamemode = %s AND user_id = %s', (*_defaults[:2], colour, _defaults[3], gamemode, user_id))
    conn.commit()

def set_panel_description(gamemode, user_id, description):
    cursor = conn.cursor()
    cursor.execute('INSERT IGNORE INTO trainers (gamemode, user_id, ign, price, colour, description) VALUES (%s, %s, %s, %s, %s, %s)', (gamemode, user_id, *_defaults[:4]))
    cursor.execute('UPDATE trainers SET ign = COALESCE(ign, %s), price = COALESCE(price, %s), colour = COALESCE(colour, %s), description = %s WHERE gamemode = %s AND user_id = %s', (*_defaults[:3], description, gamemode, user_id))
    conn.commit()

def add_ticket(channel_id, trainer_id, customer_id, gamemode):
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO tickets (channel_id, trainer_id, customer_id, gamemode) VALUES (%s, %s, %s, %s)', (channel_id, trainer_id, customer_id, gamemode))
    conn.commit()

def get_ticket_info(channel_id):
    cursor = conn.cursor()
    cursor.execute('SELECT trainer_id, customer_id, gamemode FROM tickets WHERE channel_id = %s', (channel_id,))
    row = cursor.fetchone()
    return {"trainer_id": row[0], "customer_id": row[1], "gamemode": row[2]} if row else None

def remove_ticket(channel_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tickets WHERE channel_id = %s', (channel_id,))
    conn.commit()

def get_trainer_ign(gamemode, trainer_id):
    cursor = conn.cursor()
    cursor.execute('SELECT ign FROM trainers WHERE gamemode = %s AND user_id = %s', (gamemode, trainer_id))
    row = cursor.fetchone()
    return row[0] if row else None

def toggle_active(gamemode, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT active FROM trainers WHERE gamemode = %s AND user_id = %s', (gamemode, user_id))
    row = cursor.fetchone()
    current_active = 1 if (row and row[0]) else 0
    new_active = 0 if current_active else 1
    cursor.execute('UPDATE trainers SET active = %s WHERE gamemode = %s AND user_id = %s', (new_active, gamemode, user_id))
    conn.commit()
    return bool(new_active)

def increment_lessons(gamemode, user_id):
    cursor = conn.cursor()
    cursor.execute('UPDATE trainers SET lessons = COALESCE(lessons, 0) + 1 WHERE gamemode = %s AND user_id = %s', (gamemode, user_id))
    conn.commit()
