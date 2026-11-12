"""Guard-rails in code: check and fix what the LLM returned. Never trust it blindly."""

import logging
import re

from app.enrich.schema import JobProfile
from app.models import Job
from app.shared.skills import normalise_skills

logger = logging.getLogger(__name__)

_EMAIL_SHAPE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_profile(profile: JobProfile, job: Job) -> JobProfile:
    """Return the profile with names normalised and anything invented removed."""
    # 1. Languages: "english " -> "English", no duplicates
    profile.languages_required = sorted({lang.strip().title() for lang in profile.languages_required})

    # 2. Skill names: one spelling each. Spoken languages ("German") are not skills:
    #    the LLM sometimes puts them in must_have, so we remove them there.
    languages = {lang.lower() for lang in profile.languages_required}

    def only_skills(names: list[str]) -> list[str]:
        return [s for s in normalise_skills(names) if s.lower() not in languages]

    profile.skills = only_skills(profile.skills)
    profile.must_have = only_skills(profile.must_have)
    profile.nice_to_have = only_skills(profile.nice_to_have)

    # 3. apply_email must look like an email AND really appear in the posting text.
    #    (Never guess or build an email address.)
    if profile.apply_email:
        email = profile.apply_email.strip()
        if not _EMAIL_SHAPE.match(email) or email.lower() not in job.description.lower():
            logger.info("Dropped apply_email %r for job %s: not in posting", email, job.id)
            profile.apply_email = None
        else:
            profile.apply_email = email

    return profile
