import sqlite3

class Database:
    def __init__(self, db_path="muhammadali.db"):
        self.db_path = db_path
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.connect() as conn:
            # Foydalanuvchilar
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Adminlar
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Kontent (video, fayl, matn)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section TEXT,
                    content_type TEXT,
                    file_id TEXT,
                    caption TEXT,
                    added_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        self.create_test_tables()
        self.create_teacher_tables()

    # ── USERS ──
    def add_user(self, user_id, full_name, username):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, full_name, username) VALUES (?,?,?)",
                (user_id, full_name, username)
            )
            conn.commit()

    def get_all_users(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM users").fetchall()]

    def get_stats(self):
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            today = conn.execute(
                "SELECT COUNT(*) FROM users WHERE DATE(created_at)=DATE('now')"
            ).fetchone()[0]
            return {"total": total, "today": today}

    # ── ADMINS ──
    def is_admin(self, user_id, super_admins):
        if user_id in super_admins:
            return True
        with self.connect() as conn:
            row = conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
            return row is not None

    def add_admin(self, user_id, full_name):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO admins (user_id, full_name) VALUES (?,?)",
                (user_id, full_name)
            )
            conn.commit()

    def remove_admin(self, user_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
            conn.commit()

    def get_admins(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM admins").fetchall()]

    # ── CONTENT ──
    def add_content(self, section, content_type, file_id, caption, added_by):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO content (section, content_type, file_id, caption, added_by) VALUES (?,?,?,?,?)",
                (section, content_type, file_id, caption, added_by)
            )
            conn.commit()

    def get_content(self, section):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM content WHERE section=? ORDER BY created_at DESC",
                (section,)
            ).fetchall()]

    def delete_content(self, content_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM content WHERE id=?", (content_id,))
            conn.commit()

    def get_content_by_id(self, content_id):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM content WHERE id=?", (content_id,)).fetchone()
            return dict(row) if row else None

    # ── TESTLAR ──
    def create_test_tables(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE,
                    title TEXT,
                    pdf_file_id TEXT,
                    answers TEXT,
                    question_count INTEGER DEFAULT 30,
                    added_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_test(self, code, title, pdf_file_id, answers, question_count, added_by):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tests (code, title, pdf_file_id, answers, question_count, added_by) VALUES (?,?,?,?,?,?)",
                (code, title, pdf_file_id, answers, question_count, added_by)
            )
            conn.commit()

    def get_test(self, code):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM tests WHERE code=?", (code,)).fetchone()
            return dict(row) if row else None

    def get_all_tests(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM tests ORDER BY created_at DESC").fetchall()]

    def delete_test(self, code):
        with self.connect() as conn:
            conn.execute("DELETE FROM tests WHERE code=?", (code,))
            conn.commit()

    # ── O'QITUVCHILAR ──
    def create_teacher_tables(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    subject TEXT,
                    username TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # teachers uchun tests table da teacher_id ustuni qo'shish
            try:
                conn.execute("ALTER TABLE tests ADD COLUMN teacher_id INTEGER")
            except:
                pass
            conn.commit()

    def is_teacher(self, user_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM teachers WHERE user_id=? AND status='active'", (user_id,)
            ).fetchone()
            return row is not None

    def add_teacher(self, user_id, full_name, subject, username):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO teachers (user_id, full_name, subject, username) VALUES (?,?,?,?)",
                (user_id, full_name, subject, username)
            )
            conn.commit()

    def get_teacher(self, user_id):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM teachers WHERE user_id=?", (user_id,)).fetchone()
            return dict(row) if row else None

    def get_all_teachers(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM teachers ORDER BY created_at DESC").fetchall()]

    def remove_teacher(self, user_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM teachers WHERE user_id=?", (user_id,))
            conn.commit()

    def add_teacher_test(self, code, title, pdf_id, answers, count, teacher_id):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tests (code, title, pdf_file_id, answers, question_count, added_by, teacher_id) VALUES (?,?,?,?,?,?,?)",
                (code, title, pdf_id, answers, count, teacher_id, teacher_id)
            )
            conn.commit()

    def get_teacher_tests(self, teacher_id):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM tests WHERE teacher_id=? ORDER BY created_at DESC", (teacher_id,)
            ).fetchall()]

    def save_test_result(self, user_id, full_name, region, phone, grade, test_code, correct, wrong, total, percentage, ball):
        with self.connect() as conn:
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        full_name TEXT,
                        region TEXT,
                        phone TEXT,
                        grade TEXT,
                        test_code TEXT,
                        correct INTEGER,
                        wrong INTEGER,
                        total INTEGER,
                        percentage REAL,
                        ball REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            except:
                pass
            conn.execute(
                """INSERT INTO test_results
                (user_id, full_name, region, phone, grade, test_code, correct, wrong, total, percentage, ball)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (user_id, full_name, region, phone, grade, test_code, correct, wrong, total, percentage, ball)
            )
            conn.commit()

    def get_test_results(self, test_code=None, teacher_id=None):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            if test_code:
                rows = conn.execute(
                    "SELECT * FROM test_results WHERE test_code=? ORDER BY created_at DESC", (test_code,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM test_results ORDER BY created_at DESC LIMIT 100"
                ).fetchall()
            return [dict(r) for r in rows]

    def add_test_video(self, test_code, video_file_id, caption, added_by):
        with self.connect() as conn:
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS test_videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_code TEXT UNIQUE,
                        video_file_id TEXT,
                        caption TEXT,
                        added_by INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            except:
                pass
            conn.execute(
                "INSERT OR REPLACE INTO test_videos (test_code, video_file_id, caption, added_by) VALUES (?,?,?,?)",
                (test_code, video_file_id, caption, added_by)
            )
            conn.commit()

    def get_test_video(self, test_code):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    "SELECT * FROM test_videos WHERE test_code=?", (test_code,)
                ).fetchone()
                return dict(row) if row else None
            except:
                return None

    def delete_teacher_test(self, code, teacher_id):
        with self.connect() as conn:
            conn.execute("DELETE FROM tests WHERE code=? AND teacher_id=?", (code, teacher_id))
            conn.commit()
