"""
Password Vault - v1.0.0
------------------------
Basic password generator (no storage yet — that's coming in v2.0.0).

Takes a 4-letter word and builds a 10-12 character password around it:
the 4 letters appear in the SAME ORDER as typed, dropped into random
positions in the output string. Every other slot is filled with a
random digit or special character.

Example:
    Lily  ->  L*i58l=y~1
    Fate  ->  F608a#t!<e
"""

import random
import string

SPECIAL_CHARS = "!@#$%^&*()_+-=<>?~"
FILL_POOL = string.digits + SPECIAL_CHARS

# random.SystemRandom draws from the OS's CSPRNG (os.urandom) instead of
# the default pseudo-random generator, so it's suitable for passwords.
_rng = random.SystemRandom()


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

    # Pick 4 distinct slots out of `length`, then sort them so the
    # letters land in the same left-to-right order as the input word.
    letter_positions = sorted(_rng.sample(range(length), 4))

    chars = [""] * length
    for pos, letter in zip(letter_positions, word):
        chars[pos] = letter

    for i in range(length):
        if chars[i] == "":
            chars[i] = _rng.choice(FILL_POOL)

    return "".join(chars)


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
    print("=== Password Vault v1.0.0 — basic generator ===")
    while True:
        word = input("\nEnter a 4-letter word to base the password on (or 'q' to quit): ").strip()
        if word.lower() == "q":
            print("Goodbye!")
            break
        length = _prompt_length()
        try:
            password = generate_password(word, length)
            print(f"Generated password: {password}")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
