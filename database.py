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
                    balance INTEGER DEFAULT 0,
                    is_premium INTEGER DEFAULT 0,
                    umm_coins INTEGER DEFAULT 0,
                    referred_by INTEGER DEFAULT NULL,
                    premium_until TEXT DEFAULT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            try:
                conn.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0")
            except:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
            except:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN umm_coins INTEGER DEFAULT 0")
            except:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL")
            except:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN premium_until TEXT DEFAULT NULL")
            except:
                pass
            # Referal log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS referral_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    reward_type TEXT,
                    coins INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # To'lov so'rovlari
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    months INTEGER,
                    status TEXT DEFAULT 'pending',
                    photo_file_id TEXT,
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
                    is_free INTEGER DEFAULT 1,
                    added_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Mavjud tablega ustun qo'shish (agar yo'q bo'lsa)
            try:
                conn.execute("ALTER TABLE content ADD COLUMN is_free INTEGER DEFAULT 1")
            except:
                pass
            conn.commit()
        self.create_test_tables()
        self.create_teacher_tables()

    # ── USERS ──
    def get_user(self, user_id):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def is_profile_complete(self, user_id):
        """Foydalanuvchi profili to'ldirilganmi?"""
        user = self.get_user(user_id)
        if not user:
            return False
        return bool(user.get('full_name') and user.get('region') and 
                   user.get('phone') and user.get('grade'))

    def update_profile(self, user_id, full_name, region, phone, grade):
        with self.connect() as conn:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN region TEXT")
            except: pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            except: pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN grade TEXT")
            except: pass
            conn.execute(
                "UPDATE users SET full_name=?, region=?, phone=?, grade=? WHERE user_id=?",
                (full_name, region, phone, grade, user_id)
            )
            conn.commit()

    def add_user(self, user_id, full_name, username):
        """Foydalanuvchini qo'shadi. True qaytarsa — yangi foydalanuvchi."""
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT user_id FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            if existing:
                return False  # Eski foydalanuvchi
            conn.execute(
                "INSERT INTO users (user_id, full_name, username) VALUES (?,?,?)",
                (user_id, full_name, username)
            )
            conn.commit()
            return True  # Yangi foydalanuvchi

    def is_already_referred(self, user_id):
        """Bu foydalanuvchi allaqachon referal orqali kelganmi?"""
        with self.connect() as conn:
            row = conn.execute(
                "SELECT referred_by FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            return bool(row and row[0] is not None)

    def set_referred_by_safe(self, new_user_id, referrer_id):
        """
        Referal faqat bir marta va faqat yangi foydalanuvchi uchun.
        True qaytarsa — muvaffaqiyatli.
        """
        with self.connect() as conn:
            # 1. Foydalanuvchi haqiqatan yangi bo'lishi kerak
            user_row = conn.execute(
                "SELECT referred_by, created_at FROM users WHERE user_id=?", (new_user_id,)
            ).fetchone()
            if not user_row:
                return False  # Foydalanuvchi topilmadi
            if user_row[0] is not None:
                return False  # Allaqachon referal bor

            # 2. O'zini o'zi taklif qila olmaydi
            if new_user_id == referrer_id:
                return False

            # 3. Referrer mavjudmi?
            ref_row = conn.execute(
                "SELECT user_id FROM users WHERE user_id=?", (referrer_id,)
            ).fetchone()
            if not ref_row:
                return False

            # 4. Bir xil referral log yozilganmi?
            dup = conn.execute(
                "SELECT id FROM referral_log WHERE referrer_id=? AND referred_id=?",
                (referrer_id, new_user_id)
            ).fetchone()
            if dup:
                return False

            # Hammasi tekshirildi — saqlash
            conn.execute(
                "UPDATE users SET referred_by=? WHERE user_id=?",
                (referrer_id, new_user_id)
            )
            conn.commit()
            return True

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
    def add_content(self, section, content_type, file_id, caption, added_by, is_free=1):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO content (section, content_type, file_id, caption, is_free, added_by) VALUES (?,?,?,?,?,?)",
                (section, content_type, file_id, caption, is_free, added_by)
            )
            conn.commit()

    def get_free_content(self, section):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM content WHERE section=? AND is_free=1 ORDER BY created_at DESC",
                (section,)
            ).fetchall()]

    def get_paid_content(self, section):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM content WHERE section=? AND is_free=0 ORDER BY created_at DESC",
                (section,)
            ).fetchall()]

    def is_premium(self, user_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT is_premium FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            return bool(row[0]) if row else False

    def set_premium(self, user_id, status=True):
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET is_premium=? WHERE user_id=?",
                (int(status), user_id)
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

    # ── UMM TANGA TIZIMI ──

    def get_umm(self, user_id):
        with self.connect() as conn:
            row = conn.execute("SELECT umm_coins FROM users WHERE user_id=?", (user_id,)).fetchone()
            return row[0] if row else 0

    def add_umm(self, user_id, amount, reason=""):
        with self.connect() as conn:
            conn.execute("UPDATE users SET umm_coins = umm_coins + ? WHERE user_id=?", (amount, user_id))
            conn.commit()

    def spend_umm(self, user_id, amount):
        with self.connect() as conn:
            current = conn.execute("SELECT umm_coins FROM users WHERE user_id=?", (user_id,)).fetchone()
            if not current or current[0] < amount:
                return False
            conn.execute("UPDATE users SET umm_coins = umm_coins - ? WHERE user_id=?", (amount, user_id))
            conn.commit()
            return True

    def add_referral(self, referrer_id, referred_id, reward_type, coins):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO referral_log (referrer_id, referred_id, reward_type, coins) VALUES (?,?,?,?)",
                (referrer_id, referred_id, reward_type, coins)
            )
            conn.commit()

    def get_referral_count(self, user_id):
        with self.connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM referral_log WHERE referrer_id=? AND reward_type='join'",
                (user_id,)
            ).fetchone()[0]



    def activate_premium_with_umm(self, user_id):
        from datetime import datetime, timedelta
        until = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?",
                (until, user_id)
            )
            conn.commit()

    def add_payment_request(self, user_id, amount, months, photo_id):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO payment_requests (user_id, amount, months, photo_file_id) VALUES (?,?,?,?)",
                (user_id, amount, months, photo_id)
            )
            conn.commit()

    def get_pending_payments(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM payment_requests WHERE status='pending' ORDER BY created_at DESC"
            ).fetchall()]

    def approve_payment(self, payment_id, user_id, months):
        from datetime import datetime, timedelta
        until = (datetime.now() + timedelta(days=30*months)).strftime("%Y-%m-%d")
        with self.connect() as conn:
            conn.execute("UPDATE payment_requests SET status='approved' WHERE id=?", (payment_id,))
            conn.execute(
                "UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?",
                (until, user_id)
            )
            conn.commit()

    def reject_payment(self, payment_id):
        with self.connect() as conn:
            conn.execute("UPDATE payment_requests SET status='rejected' WHERE id=?", (payment_id,))
            conn.commit()

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

    def get_user_test_results(self, user_id, limit=5):
        """Foydalanuvchining oxirgi test natijalarini olish"""
        try:
            with self.connect() as conn:
                conn.row_factory = sqlite3.Row
                # Jadval yo'q bo'lsa yaratamiz
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
                return [dict(r) for r in conn.execute(
                    "SELECT * FROM test_results WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit)
                ).fetchall()]
        except:
            return []

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
