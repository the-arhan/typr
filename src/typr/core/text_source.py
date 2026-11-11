"""Text generation and source management for Typr.

Provides word lists, quote retrieval, and code snippet loading
with natural punctuation, capitalization, and numbers support.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List, Optional

DATA_DIR = Path(__file__).parent.parent / "data"
WORDLISTS_DIR = DATA_DIR / "wordlists"
SNIPPETS_DIR = DATA_DIR / "snippets"

FALLBACK_WORDS = [
    "about", "above", "across", "action", "activity", "after", "again", "almost",
    "alone", "already", "always", "another", "answer", "anyone", "anything",
    "appear", "apply", "around", "arrive", "artist", "assume", "attack", "author",
    "become", "before", "begin", "behavior", "behind", "believe", "benefit",
    "better", "between", "beyond", "billion", "brother", "budget", "build",
    "business", "camera", "campaign", "capital", "career", "central", "century",
    "certain", "chair", "challenge", "chance", "change", "character", "charge",
    "choose", "citizen", "clearly", "college", "company", "compare", "computer",
    "concern", "condition", "consider", "continue", "control", "country", "course",
    "create", "culture", "current", "customer", "daughter", "decision", "describe",
    "design", "detail", "determine", "develop", "device", "differ", "dinner",
    "direction", "discover", "discuss", "disease", "doctor", "during", "economic",
    "education", "effect", "effort", "either", "election", "element", "employee",
    "energy", "enough", "entire", "especially", "establish", "evening", "evidence",
    "example", "executive", "expect", "expert", "explain", "factor", "family",
    "federal", "feeling", "figure", "finally", "financial", "finger", "finish",
    "follow", "foreign", "forget", "former", "forward", "friend", "future",
    "general", "generation", "government", "growth", "happen", "health", "history",
    "hospital", "however", "hundred", "husband", "identify", "imagine", "impact",
    "important", "improve", "include", "increase", "indeed", "indicate", "industry",
    "information", "inside", "instead", "interest", "international", "interview",
    "investment", "involve", "kitchen", "knowledge", "language", "lawyer", "leader",
    "letter", "likely", "listen", "little", "machine", "magazine", "maintain",
    "majority", "management", "manager", "material", "measure", "medical", "meeting",
    "member", "memory", "mention", "message", "method", "middle", "military",
    "million", "minute", "mission", "modern", "moment", "morning", "movement",
    "national", "natural", "nearly", "necessary", "network", "newspaper", "nothing",
    "notice", "number", "officer", "official", "operation", "opportunity", "option",
    "organization", "outside", "participant", "particular", "partner", "patient",
    "pattern", "perform", "performance", "perhaps", "period", "person", "personal",
    "picture", "player", "police", "policy", "political", "popular", "population",
    "position", "positive", "possible", "practice", "prepare", "present", "president",
    "pressure", "prevent", "private", "probably", "problem", "process", "produce",
    "product", "production", "professional", "professor", "program", "project",
    "property", "protect", "provide", "public", "purpose", "quality", "question",
    "quickly", "reality", "realize", "really", "reason", "receive", "recent",
    "recognize", "record", "reduce", "reflect", "region", "relate", "relationship",
    "religious", "remain", "remember", "remove", "report", "represent", "require",
    "research", "resource", "respond", "response", "responsibility", "result",
    "return", "reveal", "safety", "science", "scientist", "season", "second",
    "section", "security", "senior", "series", "serious", "service", "several",
    "shoulder", "significant", "similar", "simple", "simply", "single", "sister",
    "situation", "social", "society", "soldier", "somebody", "someone", "something",
    "sometimes", "southern", "special", "specific", "speech", "standard", "statement",
    "station", "strategy", "street", "strong", "structure", "student", "subject",
    "success", "successful", "suddenly", "suffer", "suggest", "summer", "support",
    "surface", "system", "teacher", "technology", "television", "themselves",
    "theory", "thought", "thousand", "threat", "throughout", "together", "tonight",
    "toward", "traditional", "training", "travel", "treatment", "trouble", "understand",
    "various", "victim", "violence", "weapon", "weight", "western", "whatever",
    "whether", "window", "without", "wonder", "worker", "writer", "yourself",
]


class TextSource:
    """Provides generated text streams for typing tests."""

    def __init__(
        self,
        wordlist_name: str = "english",
        punctuation: bool = False,
        numbers: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        self.wordlist_name = wordlist_name
        self.punctuation = punctuation
        self.numbers = numbers
        self._rng = random.Random(seed)
        self._words = self._load_wordlist(wordlist_name)
        self._capitalize_next = True

    def _load_wordlist(self, name: str) -> List[str]:
        path = WORDLISTS_DIR / f"{name}.txt"
        if path.is_file():
            try:
                words = [w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip()]
                if words:
                    return words
            except OSError:
                pass
        return FALLBACK_WORDS

    def generate_words(self, count: int) -> List[str]:
        """Generate a specified number of words with active formatting rules."""
        results: List[str] = []
        for _ in range(count):
            results.append(self._next_word(results[-1] if results else None))
        return results

    def _next_word(self, prev_word: Optional[str]) -> str:
        # Number generation (approx 10% chance when numbers mode is active)
        if self.numbers and self._rng.random() < 0.10:
            return str(self._rng.randint(0, 10 ** self._rng.randint(1, 4)))

        # Avoid immediate repetition
        while True:
            word = self._rng.choice(self._words)
            if prev_word is None or word != prev_word.rstrip(".,?!;:\"'").lower():
                break

        if self.punctuation:
            if self._capitalize_next:
                word = word.capitalize()
                self._capitalize_next = False

            roll = self._rng.random()
            if roll < 0.08:
                word += ","
            elif roll < 0.14:
                word += "."
                self._capitalize_next = True
            elif roll < 0.17:
                word += "?"
                self._capitalize_next = True
            elif roll < 0.19:
                word += "!"
                self._capitalize_next = True
            elif roll < 0.22:
                word = f'"{word}"'

        return word


def load_quotes() -> List[dict]:
    """Load curated quotes from package assets."""
    path = SNIPPETS_DIR / "quotes.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return [
        {"text": "Simplicity is prerequisite for reliability.", "source": "Edsger W. Dijkstra"},
        {"text": "First, solve the problem. Then, write the code.", "source": "John Johnson"},
    ]


def load_code_snippets(language: str) -> List[str]:
    """Load code snippets for a target programming language."""
    path = SNIPPETS_DIR / "code_snippets.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if language in data and data[language]:
                return data[language]
        except (OSError, json.JSONDecodeError):
            pass
    return ["def hello_world():\n    print('Hello, Typr!')"]

