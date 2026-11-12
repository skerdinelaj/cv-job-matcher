"""Skill name normalisation: "reactjs", "React.js" and "react" all become "React".

The LLM writes skills in many ways. We fix the names in CODE (not in the prompt),
so matching later compares like with like. Add aliases here when you see new ones.
"""

# key: lowercase variant  ->  value: the one name we use
SKILL_ALIASES: dict[str, str] = {
    # JavaScript world
    "js": "JavaScript",
    "javascript": "JavaScript",
    "es6": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "vue": "Vue",
    "vuejs": "Vue",
    "vue.js": "Vue",
    "angular": "Angular",
    "angularjs": "Angular",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    # Python / AI
    "python": "Python",
    "python3": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "generative ai": "Generative AI",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "retrieval-augmented generation": "RAG",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    # Data / infra
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "golang": "Go",
    "go": "Go",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "docker": "Docker",
}


def normalise_skill(name: str) -> str:
    """Return the canonical name, or the cleaned original if we don't know it."""
    cleaned = " ".join(name.split())  # trim + collapse spaces
    return SKILL_ALIASES.get(cleaned.lower(), cleaned)


def normalise_skills(names: list[str]) -> list[str]:
    """Normalise every skill and remove duplicates (case-insensitive), keeping order."""
    seen: set[str] = set()
    result: list[str] = []
    for name in names:
        skill = normalise_skill(name)
        if skill and skill.lower() not in seen:
            seen.add(skill.lower())
            result.append(skill)
    return result
