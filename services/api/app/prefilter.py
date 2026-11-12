"""Cheap rules in CODE that decide some jobs without calling the LLM.

Why: the free Gemini tier allows only ~20 requests per day. Many jobs are
obviously out for me (posting written in German, or "USA only"), so we
record that directly and save the LLM for jobs that might fit.

Every function here is pure (text in, answer out): easy to test.
"""

import re

# --- 1. Posting language ---------------------------------------------------
# Small, very common words. A German posting is full of "und", "wir", "mit"...
_GERMAN_WORDS = {
    "und", "der", "die", "das", "wir", "mit", "für", "du", "dich", "dein", "deine",
    "ist", "bei", "von", "zu", "auf", "ein", "eine", "unser", "unsere", "sie", "oder",
    "auch", "nicht", "sind", "werden", "kenntnisse", "erfahrung",
}  # fmt: skip
_ENGLISH_WORDS = {
    "the", "and", "you", "we", "with", "for", "to", "of", "our", "your", "is", "are",
    "will", "be", "experience", "team", "this", "on",
}  # fmt: skip
_WORD = re.compile(r"[a-zäöüß]+")


def detect_german(text: str) -> bool:
    """True if the text is mostly German (counts common German vs English words)."""
    words = _WORD.findall(text.lower())
    if len(words) < 40:  # too short to judge (e.g. RemoteOK teasers): let the LLM decide
        return False
    german = sum(1 for w in words if w in _GERMAN_WORDS)
    english = sum(1 for w in words if w in _ENGLISH_WORDS)
    return german > 2 * english


# --- 2. Location field --------------------------------------------------------
# Places that clearly do NOT include Albania. If the location field lists ONLY these,
# the job is country_restricted. Anything unknown -> we don't decide (the LLM does).
_NOT_FOR_ALBANIA = {
    "usa", "us", "u.s.", "united states", "america", "north america", "canada",
    "latam", "latin america", "south america", "americas", "mexico", "brazil",
    "argentina", "colombia", "chile", "peru", "india", "philippines", "pakistan",
    "australia", "new zealand", "apac", "asia", "singapore", "japan", "china",
    "south africa", "nigeria", "kenya", "israel", "saudi arabia", "uae",
}  # fmt: skip
_FILLER = re.compile(r"\b(only|time ?zones?|timezones?|remote|based)\b")


def location_is_outside_reach(location: str | None) -> bool:
    """True if the location field lists only places that exclude Albania.

    "USA"                          -> True
    "USA, Canada, USA timezones"   -> True
    "Europe, USA, Canada"          -> False (Europe is in it)
    "Worldwide" / "Berlin" / None  -> False (not sure: let the LLM decide)
    """
    if not location:
        return False
    parts = re.split(r"[,/;|]| or | and ", location.lower())
    places = [" ".join(_FILLER.sub(" ", p).split()) for p in parts]
    places = [p for p in places if p]
    return bool(places) and all(p in _NOT_FOR_ALBANIA for p in places)
