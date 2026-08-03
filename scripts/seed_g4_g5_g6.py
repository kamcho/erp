"""Seed Grades 4-6 Amber/Indigo from fee sheets (img7-10). '-' = 0."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from core.models import School, Grade, Class, Student, StudentProfile

FEMALE_FIRST = {
    "CIENNA", "FAITH", "TASMIN", "PRINCESS", "JOY", "ANN", "TIFFANY", "ABIGAEL",
    "BERNICE", "SHANTEL", "PERPETUA", "MONICA", "PRECIOUS", "KYLAH", "SARAH",
    "SHAYNE", "ANGEL", "MALIA", "AMIRA", "CINDY", "JENNIFER", "ZAINAB", "IMELA",
    "OLIVE", "DESTINY", "MARISSA", "VANESSA", "LISAH", "STACY", "TAMARA", "TATIANA",
    "BIANNA", "GABRIELLA", "MEGAN", "PAULINE", "BLESSING", "ATTIA", "TRIZAH",
    "SUBIRA", "BRIDGET", "MERCY", "RAHMA", "HASBAY", "KAITLINE", "LOVELYNE",
    "AMAYA", "SHALOM", "MUNIRA", "SASHA", "TERESA", "UMULKHEIR", "LYNN", "IRENE",
    "FAITH", "SHERRY", "ANGEL", "NAJRA", "TRACY", "VELMA", "SHANNEL", "JOY",
    "DEONNE", "SAMIRA", "ABIGAEL", "TABITHA", "JAMELIA", "CAITLYNN", "CANDICE",
    "MELISAH", "BRITNEY", "RENEE", "STEPHANIE", "MARGARET", "ARIEL", "REGINA",
    "SPECIOSA", "SAMARA", "RACHAEL", "GIFT", "VALARIE", "JANE", "LUCY", "NATASHA",
    "JOYLINE", "VICTORIA", "ALEXIS", "ESTHER", "NERIA", "VICKY", "HANIFA",
    "SHARLEEN", "PENDO", "LISA", "MEGHAN", "NADIA", "ALISHA", "MARY", "DAVINA",
}

BATCHES = [
    (
        "Grade 4",
        "Amber",
        date(2016, 6, 1),
        [
            ("3314", "SAMARA MARTHA ASAKA", 0),
            ("3319", "RACHAEL WANGARI", 0),
            ("3328", "GIFT WANGU GITU", 0),
            ("3348", "PRECIOUS NTIYARI", 0),
            ("3361", "VALARIE KYALO", 0),
            ("3368", "JANE WANJIRU MUGAI", 2400),
            ("3379", "MAX BARAKA", 0),
            ("3435", "LUCY WANJIKU", 0),
            ("3444", "BLESSING NGUMI", 7800),
            ("3450", "CARLTON MORARA", 0),
            ("3456", "DAVID MWERI AMWAYI", 20300),
            ("3485", "SAMUEL GACHINA MWANGI", 0),
            ("3503", "ALVIN GRIFFIN ODHIAMBO", 0),
            ("3608", "EMMANUEL KIPKOECH KEMBC", 0),
            ("3620", "NATASHA WANJIRU GATHI", 0),
            ("3631", "JOYLINE REINA", 0),
            ("3640", "AUSTINE KIBET KEMBOI", 0),
            ("3676", "VICTORIA NYABOKE", -5750),
            ("3682", "ALEXIS WANJIKU NJOKI", 0),
            ("3693", "LLOYD BASEL MUTHOKA", 0),
            ("3746", "ESTHER WAIRIMU MWANGI", 7500),
            ("3785", "PAUL MUGANE", 0),
            ("3879", "LOUIS KAMAU KONGONI", 0),
            ("3961", "JAYDAN MAINA MUCHANGI", 6000),
            ("3962", "FORTUNE KIMEU KITUVA", 6900),
            ("4018", "NERIA OWANDO", 5800),
            ("4096", "VICKY CHEBET", 0),
            ("4117", "HANIFA AYUMA", 0),
            ("4138", "SHARLEEN FAVOUR SEYIAN", 4700),
            ("4190", "PENDO NAFULA MUTAMBO", 0),
            ("4239", "LISA WANGU IITAMBU", 0),
            ("4242", "MEGHAN KERUBO", 0),
            ("4255", "ABDIRAHMAN SHABAAAN", 0),
        ],
    ),
    (
        "Grade 4",
        "Indigo",
        date(2016, 6, 1),
        [
            ("3687", "GODWILL MAINA NDIRITU", 4000),
            ("3690", "VICTOR MURITHI MWANGI", 7100),
            ("3694", "KINGSLEY KARIRA", -500),
            ("3713", "SHARIAHIL MOHAMED", 0),
            ("3750", "NADIA NOELLE ALUSO", 0),
            ("3766", "ALISHA WANGU", 12690),
            ("3905", "PRECIOUS AHADI MAINA", 0),
            ("3926", "ZANDER NJOROGE KINYANJUI", 0),
            ("3992", "MARY MUTHONI GITHINJI", 400),
            ("4020", "DAVINA WAMBUI", 0),
            ("4085", "ALLAN MTWANA", 0),
            ("4107", "MARY WANGARI MWANGI", 14000),
            ("4144", "JADON BARAKA", -500),
            ("4169", "CIENNA KADZO LEWA", 0),
            ("4184", "FAITH WACHERA WAWERU", 0),
            ("4206", "TASMIN BISHAR", 0),
            ("4212", "PRINCESS AUDREY", 12500),
        ],
    ),
    (
        "Grade 5",
        "Amber",
        date(2015, 6, 1),
        [
            ("3095", "JOY WANJIRU KARIUKI", 0),
            ("3108", "GIDEON IKUA", 0),
            ("3119", "ANN WANGECI GITU", 0),
            ("3114", "TRAVIS JUNIOR MIYOGO", 0),
            ("3175", "TIFFANY WAMBUI WANJIRU", 100),
            ("3210", "ABIGAEL NYAKIO", 0),
            ("3281", "BERNICE WANJIKU", 0),
            ("3333", "SHANTEL CLARA", 21000),
            ("3389", "MOFFAT JOHNSON", 0),
            ("3390", "PERPETUA HOPE", 0),
            ("3404", "PHANUEL TUMAINI", 3700),
            ("3427", "MONICA WANJIRU", 0),
            ("3582", "BYRON NDUNGU", 0),
            ("3589", "PRECIOUS WANGECHI GACHUI", 3400),
            ("3685", "KYLAH WAMBUI GITAU", 0),
            ("3704", "TRAVIS ELI HAWI GENO", 0),
            ("3807", "SARAH WANJIKU", 4800),
            ("3812", "JASON KARITHI MUGO", 0),
            ("3943", "RYAN ROMANO NJERU", 0),
            ("3958", "SHAYNE NJERI MUGO", 0),
            ("3963", "RYAN KIPKOECH NGETICH", 5700),
            ("3995", "ELVIS MAINA NYAMWEYA", 0),
            ("4009", "ANGEL WANGARI MACHARIA", 0),
            ("4050", "MALIA MANGA", 20100),
            ("4095", "JAMESRICHARD KABUTHI", 0),
            ("4112", "BRIAN MOTENDE", 10700),
            ("4125", "AMIRA JIBRIL", 0),
            ("4132", "CINDY NASIEKU", 0),
            ("4142", "JENNIFER WATERI", 0),
            ("4152", "BRADLEY PETERS ANANDA", 0),
            ("4163", "DAMIAN MBURU KAMAU", -2100),
            ("4178", "LEWIS MACHIRA WARIGIA", 0),
            ("4205", "ZAINAB BISHAR", 0),
            ("4225", "IMELA ZAWADI", 0),
            ("4235", "OLIVE NJERI NDUNGU", 0),
            ("4253", "DESTINY OBUNGU SEREMBE", 0),
            ("4259", "MARISSA IKENA", 9000),
            ("4264", "ABDIRAHMAN MOHAMUD", 0),
        ],
    ),
    (
        "Grade 5",
        "Indigo",
        date(2015, 6, 1),
        [
            ("3578", "VANESSA MAYA", 4350),
            ("3583", "LISAH GAKENIA NGOTHO", -700),
            # img9 STD 5 (continuation of Indigo)
            ("3587", "STACY MORAA ONDIGA", -3300),
            ("3727", "MICHAEL CHEGE", -20800),
            ("3737", "LEWIS MWANGI KURIA", -21700),
            ("3749", "VICTOR KAMAU MUCHUGU", -8100),
            ("3755", "TAMARA WAITHIRA MWAGO", 0),
            ("3798", "GREYSHAN MBUGUA", 0),
            ("3799", "HUSSEIN ABDI", 0),
            ("3840", "HASSAN ABDI", 0),
            ("3853", "TATIANA NJERI MWAURA", 0),
            ("3877", "ALVIS MACHARIA MUGANE", 0),
            ("3883", "PATRICK WAINANA", 0),
            ("3999", "PETER ELVIS KOSEN", 0),
            ("4036", "TAMARA NJOKI KIBIRA", 0),
            ("4173", "BIANNA NYAMBURA", 0),
            ("4176", "GABRIELLA WANJIKU KINYUA", 0),
            ("4265", "MEGAN CLAIRE", -26950),
        ],
    ),
    (
        "Grade 6",
        "Amber",
        date(2014, 6, 1),
        [
            ("2960", "TREVOR KIPKOECH", 0),
            ("2974", "JOHN EPHRAIM", 0),
            ("3017", "MILLBAR MWENI", 0),
            ("3060", "NATHAN NDERITU", 0),
            ("3072", "ABIGAEL WANGU MWANGI", 0),
            ("3125", "GIFTED MBURU", 0),
            ("3306", "COLLINS MAKORI", 0),
            ("3423", "TABITHA RUGURU", 0),
            ("3437", "JAMELIA TAJI", 0),
            ("3495", "JOSEPH MUTWIWA", 0),
            ("3496", "CAITLYNN CHEPKEMOI", 0),
            ("3531", "ABDHAFIDH IBRAHIM", 0),
            ("3632", "CANDICE KARAMBU NJUGUNA", 0),
            ("3691", "MELISAH CLARA", 0),
            ("3707", "AYDEN KIIRU", 0),
            ("3758", "VICTOR MAINA", 0),
            ("3796", "BRITNEY NJOKI", 0),
            ("3843", "RENEE WAMBUI", 0),
            ("3862", "GLEN SHIGALI ASONGA", 0),
            ("3882", "FRANK OTIEKO MALIMU", 0),
            ("3929", "WESLEY NGURE KIMANI", 0),
            ("3984", "STEPHANIE AKELO WANDERA", 0),
            ("3991", "MARGARET MUTHONI GITHINJ", 0),
            ("3997", "JOE SCHON MWANGI", 0),
            ("4007", "VICTOR MBUGUA NGUGI", 0),
            ("4010", "ARIEL CHANGILWA", 0),
            ("4025", "REGINA WAMBUI", 0),
            ("4057", "SPECIOSA WANJIKU NGUGI", 0),
            ("4078", "ETHAN NDUNGU NJENGA", 0),
            ("4088", "GAVIN NJUGUNA", 0),
            ("4158", "PAULINE WANJIRA", 3500),
            ("4160", "BLESSING NYAMBURA GITUAN", 0),
            ("4183", "IAN MWANGI WAWERU", 0),
        ],
    ),
    (
        "Grade 6",
        "Indigo",
        date(2014, 6, 1),
        [
            ("3470", "ATTIA MUTHONI", 0),
            ("3475", "TRIZAH WATHITHI", 0),
            ("3480", "SUBIRA WANJIKU", 0),
            ("3487", "BRIDGET NYOKABI ITEGI", 0),
            ("3493", "MERCY MUTHONI WOKABI", 6400),
            ("3494", "RAHMA HUSSEIN", 15100),
            ("3498", "GEORGE MURAGURI", 0),
            ("3514", "HASBAY NAYA", 8700),
            ("3516", "JUBAL LYSANIAS", 100),
            ("3716", "KAITLINE ELIANA", 0),
            ("3761", "WAYNE WILSHERE RICHARD", 0),
            ("3765", "LOVELYNE WANGARI MWAUR", 4800),
            ("3786", "AMAYA WANJIRA", 0),
            ("3797", "SHALOM NJERI IKENYE", 0),
            ("3836", "SAMUEL GITONGA MIRUGI", 0),
            ("3851", "MUNIRA ALINOOIR IBRAHIM", 4100),
            ("4072", "SASHA SARA KEJI", 5000),
            ("4102", "TERESA WANJIRA", 0),
            ("4124", "UMULKHEIR JIBRIL", 0),
            ("4240", "LYNN NJOKI ITAMBU", 43600),
            # additional short adm nos kept as given
            ("008", "IRENE WANJIRA", 5700),
            ("026", "JASON WARARI", 4500),
            ("029", "FAITH GRACIOUS", 0),
            ("038", "KELVIN OTENGO", 0),
            ("052", "SAMSON NJOROGE", 0),
            ("2842", "AIDAN MWANGI MIRIRU", 8000),
            ("2867", "SHERRY NJOKI", 21350),
            ("2883", "SMITH MWANGI", 4800),
            ("2946", "ANGEL WANGECHI MUTITU", -700),
            ("2984", "DELVIN MUNENE", 9300),
            ("3052", "PRECIOUS WAMBUI GITAU", 0),
            ("3214", "NAJRA ABDIAZIZ", 90200),
            ("3256", "TRACY WAMATHA KAMAU", 4800),
            ("3258", "VELMA CHEPKEMOI KOECH", 14000),
            ("3271", "SHANNEL MWIHAKI", 18500),
            ("3272", "ERIC JOHN NJUGUNA", 3100),
            ("3273", "ROBERT SAMUEL NJUGUNA", 3100),
            ("3305", "JOY NJERI NDIRANGU", 0),
            ("3447", "DEONNE KAREMBO", 0),
            ("3623", "SAMIRA ALI ADAM", 0),
        ],
    ),
]

JOINED = date(2026, 1, 5)


def split_name(full: str):
    parts = [p for p in full.strip().split() if p]
    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()
    if len(parts) == 2:
        return parts[0].title(), "", parts[1].title()
    return parts[0].title(), " ".join(parts[1:-1]).title(), parts[-1].title()


def upsert(school, klass, adm, name, bal, dob):
    first, middle, last = split_name(name)
    gender = "female" if first.upper() in FEMALE_FIRST else "male"
    student = Student.objects.filter(adm_no=str(adm)).first()
    created = False
    if not student:
        student = Student(
            adm_no=str(adm),
            first_name=first,
            middle_name=middle,
            last_name=last,
            date_of_birth=dob,
            joined_date=JOINED,
            gender=gender,
            fee_category="day",
            is_boarder=False,
        )
        created = True
    else:
        student.first_name = first
        student.middle_name = middle
        student.last_name = last
        student.gender = gender
    student.save()

    profile, _ = StudentProfile.objects.get_or_create(
        student=student,
        defaults={
            "school": school,
            "class_id": klass,
            "fee_balance": bal,
            "status": "Active",
            "discipline": 100,
        },
    )
    profile.school = school
    profile.class_id = klass
    profile.fee_balance = bal
    profile.status = "Active"
    profile.save()
    return created, student, profile


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    if not school:
        raise SystemExit("Excel Academy not found")

    created_n = updated_n = 0
    with transaction.atomic():
        for grade_name, stream, dob, rows in BATCHES:
            grade = Grade.objects.filter(name=grade_name).first()
            klass = Class.objects.filter(school=school, grade=grade, name=stream).first()
            if not klass:
                raise SystemExit(f"Missing class: {grade_name} / {stream}")
            print(f"\n{grade_name} {stream} (id={klass.id}) — {len(rows)} rows")
            for adm, name, bal in rows:
                created, student, profile = upsert(school, klass, adm, name, bal, dob)
                if created:
                    created_n += 1
                    tag = "Created"
                else:
                    updated_n += 1
                    tag = "Updated"
                print(f"  {tag}: {adm} {student.get_full_name()} balance={profile.fee_balance}")

            total = StudentProfile.objects.filter(class_id=klass).count()
            owing = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).count()
            credit = StudentProfile.objects.filter(class_id=klass, fee_balance__lt=0).count()
            print(f"  -> class total: {total} ({owing} owing, {credit} credit)")

    print(f"\nDone. Created {created_n}, updated {updated_n}.")


if __name__ == "__main__":
    run()
