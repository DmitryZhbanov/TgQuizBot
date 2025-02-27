import aiosqlite

DB_NAME = None

def set_db_name(db_name: str):
    global DB_NAME
    DB_NAME = db_name

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER
        )''')
        async with db.execute("PRAGMA table_info(quiz_state)") as cursor:
            columns = await cursor.fetchall()
        if not any(col[1] == 'score' for col in columns):
            await db.execute('ALTER TABLE quiz_state ADD COLUMN score INTEGER DEFAULT 0')
        await db.commit()

async def get_quiz_state(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result if result is not None else (0, 0)

async def update_quiz_state(user_id: int, question_index: int, score: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)',
                         (user_id, question_index, score))
        await db.commit()
