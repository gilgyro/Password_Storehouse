"""
Password Vault - v2.0.0
------------------------
Adds persistent storage: generated passwords are now saved together with
account info (account name + username) in a local SQLite database file
called accnpasskeys.db, in a table also called accnpasskeys.

Takes a 4-letter word and builds a 10-12 character password around it:
the 4 letters appear in the SAME ORDER as typed, dropped into random
positions in the output string. Every other slot is filled with a
random digit or special character.

Example:
    Lily  ->  L*i58l=y~1
    Fate  ->  F608a#t!<e
"""

import random
import sqlite3
import string
from datetime import datetime

DB_NAME = "accnpasskeys.db"
TABLE_NAME = "accnpasskeys"

SPECIAL_CHARS = "!@#$%^&*()_+-=<>?~"
FILL_POOL = string.digits + SPECIAL_CHARS

# random.SystemRandom draws from the OS's CSPRNG (os.urandom) instead of
# the default pseudo-random generator, so it's suitable for passwords.
_rng = random.SystemRandom()


def init_db():
    """Create the database file/table if they don't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            username TEXT,
            base_word TEXT NOT NULL,
            password TEXT NOT NULL,
            length INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_password(word: str, length: int = 10) -> str:
    """
    Build a password of `length` characters that contains the 4 letters
    of `word`, in order, at random positions. Remaining positions are
    filled with random digits/special characters.
    """
    if len(word) != 4 or not all(c in string.ascii_letters for c in word):
        raise ValueError("Input word must be exactly 4 letters (A-Z or a-z).")
    if length not in (10, 11, 12):
        raise ValueError("Length must be 10, 11, or 12.")

    letter_positions = sorted(_rng.sample(range(length), 4))

    chars = [""] * length
    for pos, letter in zip(letter_positions, word):
        chars[pos] = letter

    for i in range(length):
        if chars[i] == "":
            chars[i] = _rng.choice(FILL_POOL)

    return "".join(chars)


def add_entry(account_name: str, username: str, word: str, length: int = 10) -> str:
    """Generate a password and store it with the account info. Returns the password."""
    password = generate_password(word, length)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        f"""INSERT INTO {TABLE_NAME}
            (account_name, username, base_word, password, length, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
        (account_name, username, word, password, length, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    return password


def view_entries():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT id, account_name, username, password, length, created_at FROM {TABLE_NAME} ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_entry(entry_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def _prompt_length() -> int:
    raw = input("Password length (10, 11, or 12) [default 10]: ").strip()
    if not raw:
        return 10
    try:
        val = int(raw)
    except ValueError:
        print("Not a number, using 10.")
        return 10
    if val not in (10, 11, 12):
        print("Must be 10, 11, or 12 — using 10.")
        return 10
    return val


def main():
    init_db()
    while True:
        print("\n=== Password Vault v2.0.0 ===")
        print("1. Generate password & save account info")
        print("2. View saved accounts")
        print("3. Delete an account entry")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            word = input("Enter a 4-letter word to base the password on: ").strip()
            account_name = input("Account/service name (e.g. Gmail, Netflix): ").strip()
            username = input("Username/email for this account: ").strip()
            length = _prompt_length()
            try:
                password = add_entry(account_name, username, word, length)
                print(f"\nGenerated password: {password}")
                print(f"Saved to {DB_NAME} ✔")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            rows = view_entries()
            if not rows:
                print("No entries found.")
            else:
                print(f"\n{'ID':<4}{'Account':<18}{'Username':<22}{'Password':<15}{'Len':<5}{'Created At'}")
                print("-" * 80)
                for r in rows:
                    print(f"{r[0]:<4}{r[1]:<18}{r[2]:<22}{r[3]:<15}{r[4]:<5}{r[5]}")

        elif choice == "3":
            entry_id = input("Enter the ID of the entry to delete: ").strip()
            if entry_id.isdigit():
                delete_entry(int(entry_id))
                print("Entry deleted.")
            else:
                print("Invalid ID.")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
