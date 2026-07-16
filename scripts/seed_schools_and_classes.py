from core.models import School, Grade, Class

# 1. Create the three schools
schools_data = ["Excel Grassland", "Excel Woodland", "Excel Academy"]
schools = []
for name in schools_data:
    school, created = School.objects.get_or_create(name=name)
    if created:
        print(f"Created School: {name}")
    schools.append(school)

# 2. Create the grades
grade_choices = [
    'Play Group', 'PP1', 'PP2', 'Grade 1', 'Grade 2', 'Grade 3',
    'Grade 4', 'Grade 5', 'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9'
]
grades = []
for g_name in grade_choices:
    g, created = Grade.objects.get_or_create(name=g_name)
    if created:
        print(f"Created Grade: {g_name}")
    grades.append(g)

# 3. Create the classes (streams) for each school and grade
class_count = 0
for school in schools:
    for g in grades:
        if g.name in ['Play Group', 'PP1', 'PP2']:
            streams = ["Indigo"]
        elif g.name.startswith('Grade'):
            try:
                num = int(g.name.split()[-1])
                if num <= 6:
                    streams = ["Indigo", "Amber"]
                else:
                    streams = ["Tiger", "Cheetah"]
            except (ValueError, IndexError):
                streams = ["Indigo", "Amber"]
        else:
            streams = ["Indigo", "Amber"]

        for s_name in streams:
            c, created = Class.objects.get_or_create(name=s_name, grade=g, school=school)
            if created:
                class_count += 1
            
print(f"Successfully seeded {len(schools)} schools, {len(grades)} grades, and {class_count} classes/streams!")
