"""Subject field for a US major name (shared by us_majors.py and us_new5.py)."""
import re

KEYS = [("artificial intelligence", "Computer Science"), ("human-centered artificial", "Computer Science"), ("computational finance", "Finance"),
        ("integrated circuit", "Electrical and Electronic Engineering"), ("intelligent medic", "Biomedical Engineering"), ("nanomedicine", "Biomedical Science"),
        ("computer", "Computer Science"), ("comput", "Computer Science"), ("data science", "Data Science"), ("statistic", "Statistics"),
        ("mathemat", "Mathematics"), ("physics", "Physics"), ("astro", "Physics"), ("chemical eng", "Chemical Engineering"), ("engineering sciences \\(chemical", "Chemical Engineering"), ("chemi", "Chemistry"), ("biochem", "Biochemistry"),
        ("biomedical eng", "Biomedical Engineering"), ("electrical", "Electrical and Electronic Engineering"), ("mechanical", "Mechanical Engineering"),
        ("civil engineering", "Civil Engineering"), ("aerospace", "Aerospace Engineering"), ("industrial", "Engineering"), ("materials", "Engineering"),
        ("engineer", "Engineering"), ("neuro", "Neuroscience"), ("biolog", "Biology"), ("bioscien", "Biology"), ("cognitive", "Psychology"),
        ("psycholog", "Psychology"), ("econom", "Economics"), ("business", "Business"), ("management", "Business"), ("finance", "Finance"),
        ("account", "Business"), ("politic", "Politics"), ("global affairs", "International Relations"), ("international", "International Relations"),
        ("public health", "Public Health"), ("nursing", "Nursing"), ("architect", "Architecture"), ("design", "Design"), ("music", "Music"),
        ("art", "Art"), ("film", "Media and Communication"), ("media", "Media and Communication"), ("history", "History"), ("philosoph", "Philosophy"),
        ("english", "English"), ("linguist", "Linguistics"), ("sociolog", "Sociology"), ("anthropolog", "Anthropology"), ("environment", "Environmental Science"),
        ("earth", "Earth Sciences"), ("geolog", "Earth Sciences"), ("ecolog", "Biology"), ("urban", "Urban Studies"), ("law", "Law")]


def field_for(name):
    n = name.lower()
    return next((f for k, f in KEYS if re.search(rf"\b{k}", n)), name)
