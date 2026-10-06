import re
import nltk
from nltk.corpus import stopwords

try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOP_WORDS = set(stopwords.words("english"))


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+#.\s]", " ", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return " ".join(words)


def extract_skills(text, skills_list):
    text_lower = text.lower()
    found = []

    for skill in skills_list:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)

    return found
