"""Seed G6 updates + G7-G9 + PC. '-' = 0.
Stream map: A/B -> Tiger, I -> Cheetah. PC -> Grade 9 / PC.
"""
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
    "PAULINE", "BLESSING", "ATTIA", "TRIZAH", "SUBIRA", "BRIDGET", "MERCY", "RAHMA",
    "HASBAY", "KAITLINE", "LOVELYNE", "AMAYA", "SHALOM", "MUNIRA", "SASHA", "TERESA",
    "UMULKHEIR", "LYNN", "IRENE", "FAITH", "SHERRY", "ANGEL", "NAJRA", "TRACY",
    "VELMA", "SHANNEL", "JOY", "DEONNE", "SAMIRA", "NAVEEN", "JULIA", "ESTHER",
    "OPRAH", "AISHA", "HELLEN", "BUSHRA", "CYNTHIA", "LARISSA", "MARLIYA",
    "JULIE", "MELISSA", "VIVIAN", "JADE", "ELIZABETH", "ELSA", "ALYSER",
    "MITCHELLE", "LAURA", "SABRINA", "ABIGAEL", "HARIA", "JOY", "TIFFANY",
    "DIANA", "TASHLEY", "SHIRLEEN", "JEAN", "WARDA", "AGNES", "PAMELA",
    "FAVOUR", "TRACY", "PEACE", "PRECIOUS", "FAITH",
    "WHITNEY", "WINNIE", "ALEXIS", "SALMA", "LIBERTY", "SAMANTHA", "SASHA",
    "EVA", "JOY", "TAMARA", "WANDA", "BUSHRA", "PRISCAH",
    "FARAH", "STACEY", "JOY", "LEANNE", "NICE", "ANGEL",
    "ZAWADI", "ASHLEY", "REBECCA", "HOPE", "YVONNE", "TASHA", "KIMBERLY",
    "ERICAH", "AUDREY", "SHARLY", "NATASHA", "ANGELA", "IRENE", "CLARE", "CHLOE",
}

BATCHES = [
    (
        "Grade 6",
        "Amber",
        date(2014, 6, 1),
        [
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
    (
        "Grade 7",
        "Tiger",  # STD 7A
        date(2013, 6, 1),
        [
            ("3644", "NAVEEN ESTHER MAIGA", 17000),
            ("3711", "BENNY WANJOHI", 108200),
            ("3714", "SUHEIB MOHAMED", 0),
            ("3730", "STEVE KIMANI", 0),
            ("3731", "JULIA WANGAR MEWENJERI", 4800),
            ("3794", "PAUL MICKEY WACHIRA", 4800),
            ("3811", "DYLAN LEE KAMAU", 0),
            ("3817", "ZAKARIA BISHAR HUSSEIN", 0),
            ("3889", "ESTHER NJERI MUIRURI", 30000),
            ("3934", "OPRAH TATIANA", 10000),
            ("4026", "ARSENE ASEGA ODERA", 0),
            ("4045", "ABDI KHALIQ ABDI", 24500),
            ("4073", "AISHA ISMAIL", 0),
            ("4120", "HELLEN WANJIRA MWANGI", 0),
            ("4151", "BUSHRA SHABAN", 9300),
            ("4168", "IBRAHIM MUKALA", 0),
            ("4177", "BLESSING NYAMBURA WARIGI", 0),
            ("4188", "VICTOR MOSE NYABUTO", 0),
            ("4189", "CYNTHIA NJERI MAINA", 0),
            ("4198", "RANDY PHILIP KAMAU", 0),
            ("4209", "LARISSA WANJALA", 0),
            ("4214", "MARLIYA HASSAN", 0),
            ("4215", "FELIX OMONDI", 0),
            ("4223", "SIVV IRUNGU KAIKU", 0),
            ("4243", "JOY NJERI KARANJA", 0),
            ("4248", "JAMES NJENGA NGACHA", 0),
            ("4262", "MUMIN MANSOOR", 0),
        ],
    ),
    (
        "Grade 7",
        "Cheetah",  # STD 7I
        date(2013, 6, 1),
        [
            ("3294", "JULIE WAIRIMU", 28900),
            ("3330", "OLIVER OOKO", 0),
            ("3343", "MELISSA GATHIGIA KIMANI", 0),
            ("3345", "GIFT MAINA SIMON", 5900),
            ("3352", "JAMAL KROP", 0),
            ("3393", "MUAYID HASHI", 6300),
            ("3428", "VIVIAN WAIRIMU", 0),
            ("3429", "JADE TARAJI", 0),
            ("3561", "IMMANUEL AIDEN OCHIENG", 0),
            ("3719", "ELDAD JUMA HERNANDEZ", 0),
            ("3720", "HASTINGS MUNENE", 0),
            ("3957", "TREVOR MUNENE", 26900),
            ("4159", "ANGEL MUGURE JOSEPH", 0),
            ("4210", "ELIZABETH KASIVA", 0),
            ("4216", "ELSA WANJIKU MUCHIRI", 0),
            ("4224", "ALYSER NJERI MBURU", 0),
            ("4226", "FRANK MUNGAI", 0),
            ("4227", "DENZEL WAKARIA", 0),
            ("4230", "ARNOLD STEVEN", 0),
        ],
    ),
    (
        "Grade 8",
        "Tiger",  # STD 8A
        date(2012, 6, 1),
        [
            ("2780", "ELIZAPHAN KIRUKI", 13800),
            ("2781", "MITCHELLE MUMBUA", 0),
            ("2782", "DERIS CHURCHIL", -1900),
            ("2784", "LAURA WANIRU", 4500),
            ("2810", "IBRAHIM ABDIAZIZ", 93000),
            ("2853", "SABRINA WANGARI", 0),
            ("2920", "FAITH ACHIENG", 0),
            ("3081", "CLYDE MACHAYO", 8500),
            ("3101", "JAYDEN LESHIAN", -600),
            ("3120", "SAMMY LUMIRE", 4800),
            ("3129", "GALEN WEEKSA", 10500),
            ("3150", "ABIGAEL WARIMU NDEGWA", 0),
            ("3179", "ANDREW GATHIMBA", 3650),
            ("3215", "HARIA ABDIAZIZ", 0),
            ("3377", "JOY LYNNE WANIRU NJAGI", 0),
            ("3622", "MOHAMED ALI ADAM", 0),
            ("3648", "WARIO BAGAO", 0),
            ("3653", "KYLE KIPKEMOI", 0),
            ("3736", "ARTHUR MWANGI", 0),
            ("3775", "NAHASION NJERU MURUKU", 25000),
            ("3804", "PRINCEHAL DERMOT", 0),
            ("3844", "TED MAINGA", 0),
            ("3844B", "BRUCE NGANGA", 0),  # duplicate adm on sheet
            ("3856", "TIFFANY WAITHERA MATIMU", 0),
            ("3875", "DIANA CHEPKORIR ROP", 0),
            ("3897", "TASHLEY ROEL", 0),
            ("3945", "LEEAM NUGUNA", 0),
            ("3972", "SHIRLEEN NYAMBURA GITONG", 0),
            ("4001", "JEAN MAYA WANIRU", 0),
            ("4011", "AZRIEL AMISI", 0),
            ("4034", "WARDA WANIRU", 0),
            ("4049M", "MELCHIZEDEK MULI", 0),  # 4049 already used elsewhere
            ("4049A", "AGNES MUMBE", 0),
            ("4047", "ABDUL BARI MOHAMMED", 0),
            ("4048", "PAMELA AKINYI", 0),
            ("4055", "TEDDY SAM KUNJURI", 0),
            ("4070", "FAVOUR NAOMI WANIRU", 0),
            ("4084", "TRACY MAJOHO", 0),
            ("4104", "DYLAN AVI DAVIES", 0),
            ("4135", "PEACE WANGU MBATIA", 0),
            ("4157", "PRECIOUS OZIL KIKENDA", 0),
            ("4180", "PETER MWANGI NDUNGU", 0),
            ("4247", "FAITH ABELAH MAUMBA", 0),
            ("4251", "BRIGHTON GACHAU", 0),
        ],
    ),
    (
        "Grade 9",
        "Tiger",  # STD 9B
        date(2011, 6, 1),
        [
            ("2777", "MARCUS NUGUNA", 13500),
            ("2804", "MARWA ABDIAZIZ", 27100),
            ("2861", "OWEN KIPCHIRCHIR", 125700),
            ("3000", "SAMUEL OBUNGO", 18210),
            ("3093", "STEVE GERALD MUHATIA", 8000),
            ("3105", "WHITNEY SINTAMEI", 45200),
            ("3128", "WINNIE WANIKU MBAI", 2000),
            ("3142", "ETHAN NYENIERI", 0),
            ("3147", "ALEXIS CHEREMBOI", 0),
            ("3157", "MELVIN MWANGI", 23500),
            ("3188", "HARRISON NGANG'A", 0),
            ("3170", "SALMA MOHAMMED", 0),
            ("3204", "LIBERTY BRIGHT", -500),
            ("3315", "SAMANTHA MILKA ASAKA", 0),
            ("3402", "SASHA NYAMBOGO", 7500),
            ("3424", "STEVE NUGU", 0),
            ("3509", "REU MBURU KAMAU", 7000),
            ("3529", "JOSEPH MULINGE", -500),
            ("3668", "EVA WAMBUI MWANGI", 29300),
            ("3689", "JOY NJERI NJOROGE", 0),
            ("3710", "LEON LUTHER WANJANA", 0),
            ("3718", "TAMARA ALICE WANJIRA", 2400),
            ("4027", "ALVAN KARUKI MUTHONI", 9500),
            ("4042", "MOHAMED ABDURRAHMAN HAS", 3000),
            ("4062", "WANDA WANJA", 0),
            ("4100", "BUSHRA IBRAHIM", 2500),
            ("4113", "ADRIAN KAMAU", 0),
            ("4170", "NIGEL CHAI LEWA", 0),
            ("4193", "DYLAN MURITHI KIBAARA", 0),
            ("4201", "PRISCAH KEMUNTO", 9000),
            ("4228", "SEAN TREVOR RONO", 9500),
            ("4260", "AKRAM ABDISALAM", 0),
        ],
    ),
    (
        "Grade 9",
        "Cheetah",  # STD 9I
        date(2011, 6, 1),
        [
            ("2766", "FARAH ABDIAZZIZ", 0),
            ("2969", "STACEY WANJIKU KAMAU", 5000),
            ("2973", "JOY WANJIRU KAMAU", 0),
            ("2985", "VICTOR WILLIES", -30700),
            ("2999", "RYAN ABDULAHI", 27500),
            ("3152", "JOY MUTHONI WANJANA", 0),
            ("3331", "LEANNE WANGARI KIMANI", 0),
            ("3477", "BRAYSON MAINA", 0),
            ("3556", "NICE APPLESENT WAMBUI", 0),
            ("3657", "TONNY MALI SOMONI", 0),
            ("3664", "JAYDEN MATUNDA", 0),
            ("4063", "CHRISTIAN MWANGI", 6000),
            ("4114", "ANGEL MUKAMI", 16000),
            ("4261", "ABDURIZACK HASSAN", 0),
        ],
    ),
    (
        "Grade 9",
        "PC",  # STD PC — dedicated stream so data is not lost
        date(2011, 6, 1),
        [
            ("2746", "ZAWADI ZARIA", 4500),
            ("2765", "MOHAMMED ABDIAZZI", 0),
            ("2893", "LEON BLESSED", 0),
            ("2895", "SALAH MAJID", 0),
            ("2953", "JOHN AKWATA", 0),
            ("2958", "ETHAN NIDICHU KAMUYU", 12800),
            ("2962", "ASHLEY WANJIKU KAMANDE", 4500),
            ("2963", "REBECCA SHANEL", 0),
            ("2971", "JAYSON LIMO KIPCHIRCHIR", 0),
            ("2990", "SHAWNLEY OCHOKI", 0),
            ("3251", "KEITH JAYDEN KEITH", 0),
            ("3442", "HOPE WAVERU", 21400),
            ("3508", "RYAN NGUCE MURUKU", 0),
            ("3605", "ELVIS OTIENO RADOLO", 0),
            ("3645", "DENZEL KIPURU", 0),
            ("3650", "YVONNE NIKRA WAMBUI", 0),
            ("3686", "TASHA CHELANGAT", 0),
            ("3788", "KIMBERLY BOCHERE NYAMAC", 0),
            ("3826", "ERICAH NOWELL AYUMA", 0),
            ("3828", "SAMMY MURENGI MWANGI", 0),
            ("3842", "AUDREY WANGARI OSEBE", 0),
            ("3857", "SHARLY WANJIKU MATIMU", 0),
            ("3861", "NATASHA WAMUYU", 12500),
            ("3896", "ANGELA MASIKA", 5050),
            ("3902", "IRENE WAITHIRA IRUNGU", 0),
            ("3909", "CLARE WAITHIRA MUTITU", 0),
            ("4031", "MARTIN CHEGE WAMBUI", 0),
            ("4137", "MOSES BARAKA", 3000),
            ("4175", "CHLOE WANJIRU", 1000),
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


def get_or_create_class(school, grade_name, stream):
    grade = Grade.objects.filter(name=grade_name).first()
    if not grade:
        raise SystemExit(f"Missing grade: {grade_name}")
    klass = Class.objects.filter(school=school, grade=grade, name=stream).first()
    if not klass:
        klass = Class.objects.create(school=school, grade=grade, name=stream)
        print(f"Created class: {grade_name} / {stream} (id={klass.id})")
    return klass


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
            klass = get_or_create_class(school, grade_name, stream)
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
    print("Notes: 3844 Bruce -> 3844B; 4049 Melchizedek/Agnes -> 4049M/4049A (sheet dupes).")
    print("STD PC placed in Grade 9 / PC (new stream). Reassign if that is wrong.")
    print("STD 8I had no individual rows — skipped.")


if __name__ == "__main__":
    run()
