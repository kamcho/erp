"""
Seed academic year + terms for 2026 (and 2027 start).

Term dates (2026):
  Term 1: 5 Jan  – 2 Apr   (next opens 27 Apr)
  Term 2: 27 Apr – 31 Jul  (next opens 24 Aug)
  Term 3: 24 Aug – 23 Oct  (next opens 4 Jan 2027)

Academic years:
  2026: starts 5 Jan 2026
  2027: starts 4 Jan 2027
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction

from core.models import AcademicYear, Term

# closing_date = last day of this term
# opening_date = next opening (start of following term) — matches Configurations UI
TERMS_2026 = [
    {
        "name": "Term 1",
        "closing_date": date(2026, 4, 2),
        "opening_date": date(2026, 4, 27),  # Term 2 starts
        "is_active": False,
    },
    {
        "name": "Term 2",
        "closing_date": date(2026, 7, 31),
        "opening_date": date(2026, 8, 24),  # Term 3 starts
        "is_active": True,  # Aug 3 2026 is in the holiday after Term 2
    },
    {
        "name": "Term 3",
        "closing_date": date(2026, 10, 23),
        "opening_date": date(2027, 1, 4),  # Term 1 2027 starts
        "is_active": False,
    },
]

YEARS = [
    {
        "start_date": date(2026, 1, 5),
        "end_date": date(2026, 10, 23),
        "is_active": True,
    },
    {
        "start_date": date(2027, 1, 4),
        # Approx same window as 2026 Term 1 end (early April)
        "end_date": date(2027, 10, 22),
        "is_active": False,
    },
]


def upsert_year(start_date, end_date, is_active):
    year = (
        AcademicYear.objects.filter(start_date__year=start_date.year).order_by("id").first()
        or AcademicYear.objects.filter(start_date=start_date).first()
    )
    if year:
        year.start_date = start_date
        year.end_date = end_date
        year.is_active = is_active
        year.save(update_fields=["start_date", "end_date", "is_active"])
        print(f"Updated year {start_date.year}: {start_date} -> {end_date} active={is_active}")
    else:
        year = AcademicYear.objects.create(
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )
        print(f"Created year {start_date.year}: {start_date} -> {end_date} active={is_active}")
    return year


def upsert_term(name, closing_date, opening_date, is_active):
    term = Term.objects.filter(name__iexact=name).order_by("id").first()
    if term:
        term.name = name
        term.closing_date = closing_date
        term.opening_date = opening_date
        term.is_active = is_active
        term.save(update_fields=["name", "closing_date", "opening_date", "is_active"])
        print(
            f"Updated {name}: close={closing_date} next_open={opening_date} active={is_active}"
        )
    else:
        term = Term.objects.create(
            name=name,
            closing_date=closing_date,
            opening_date=opening_date,
            is_active=is_active,
        )
        print(
            f"Created {name}: close={closing_date} next_open={opening_date} active={is_active}"
        )
    return term


def run():
    with transaction.atomic():
        # Only one active academic year
        AcademicYear.objects.update(is_active=False)
        for y in YEARS:
            upsert_year(**y)

        # Only one active term; clean duplicate/extra term names for this calendar
        Term.objects.update(is_active=False)
        keep_ids = []
        for t in TERMS_2026:
            term = upsert_term(**t)
            keep_ids.append(term.id)

        # Remove loose duplicates like "Term 1 2026" if they have no useful dates
        extras = Term.objects.exclude(id__in=keep_ids).filter(
            name__iregex=r"^Term\s*[123](\s|$|20)"
        )
        for extra in extras:
            print(f"Deleting extra term: {extra.name!r} (id={extra.id})")
            extra.delete()

    print("\nCurrent state:")
    for y in AcademicYear.objects.all().order_by("start_date"):
        print(f"  Year {y.start_date} -> {y.end_date} active={y.is_active}")
    for t in Term.objects.all().order_by("id"):
        print(
            f"  {t.name}: close={t.closing_date} next_open={t.opening_date} active={t.is_active}"
        )


if __name__ == "__main__":
    run()
