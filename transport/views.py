from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Route, Vehicle, TransportAssignment
from core.models import Student, StudentProfile, School, Class, AcademicYear, Term
from django.db.models import Count, Q, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone

@login_required
def transport_dashboard(request):
    # Filter by school if user is linked to one and is not a superuser
    user_school = request.user.school if not request.user.is_superuser else None
    
    school_id = request.GET.get('school')
    class_id = request.GET.get('class')
    search_query = request.GET.get('q', '').strip()

    if user_school:
        school_id = user_school.id
        can_change_school = False
    else:
        can_change_school = True

    # Get active term and year
    active_year = AcademicYear.objects.filter(is_active=True).first()
    active_term = Term.objects.filter(is_active=True).first()

    # Fetch all students based on filters to show assignment status
    active_prefetch = Prefetch(
        'transport_assignments',
        queryset=TransportAssignment.objects.filter(is_active=True, academic_year=active_year, term=active_term),
        to_attr='active_assignment_list'
    )
    
    students_qs = Student.objects.select_related('studentprofile__class_id', 'studentprofile__school').prefetch_related(active_prefetch)
    
    # Robust Search (Name or ADM)
    if search_query:
        query_parts = search_query.split()
        for part in query_parts:
            students_qs = students_qs.filter(
                Q(first_name__icontains=part) | 
                Q(middle_name__icontains=part) | 
                Q(last_name__icontains=part) | 
                Q(adm_no__icontains=part)
            )

    # Force school filter if not superuser
    if user_school:
        students_qs = students_qs.filter(studentprofile__school=user_school)
    elif school_id:
        students_qs = students_qs.filter(studentprofile__school_id=school_id)
        
    if class_id:
        students_qs = students_qs.filter(studentprofile__class_id_id=class_id)
    
    # We need a separate list for the dropdown to ensure you can assign anyone without bringing down the server
    dropdown_qs = Student.objects.select_related('studentprofile__class_id', 'studentprofile__class_id__grade').only(
        'id', 'first_name', 'last_name', 'middle_name', 'adm_no',
        'studentprofile__class_id__name', 'studentprofile__class_id__grade__name'
    )
    if user_school:
        dropdown_qs = dropdown_qs.filter(studentprofile__school=user_school)
    elif school_id:
        dropdown_qs = dropdown_qs.filter(studentprofile__school_id=school_id)
    if class_id:
        dropdown_qs = dropdown_qs.filter(studentprofile__class_id_id=class_id)
    if search_query:
        query_parts = search_query.split()
        for part in query_parts:
            dropdown_qs = dropdown_qs.filter(
                Q(first_name__icontains=part) | 
                Q(middle_name__icontains=part) | 
                Q(last_name__icontains=part) | 
                Q(adm_no__icontains=part)
            )

    dropdown_students = dropdown_qs.order_by('first_name')[:30]

    if not school_id and not class_id and not user_school and not search_query:
        # Default view for superadmins: only show assigned (to avoid massive tables)
        students_qs = students_qs.filter(transport_assignments__is_active=True, transport_assignments__academic_year=active_year, transport_assignments__term=active_term)

    # Sort students: name
    students_qs = students_qs.distinct().order_by('first_name')
    
    # Pagination
    paginator = Paginator(students_qs, 100)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    # Process students to add active_assignment helper
    for student in students:
        student.active_transport = student.active_assignment_list[0] if student.active_assignment_list else None

    # Stats logic
    all_active_assignments = TransportAssignment.objects.filter(is_active=True, academic_year=active_year, term=active_term)
    if school_id:
        all_active_assignments = all_active_assignments.filter(student__studentprofile__school_id=school_id)
    if class_id:
        all_active_assignments = all_active_assignments.filter(student__studentprofile__class_id_id=class_id)
    
    total_assigned = all_active_assignments.count()
    
    # Prepare students for new assignments dropdown (must be unassigned in CURRENT term)
    
    # Fetch filter options
    if not request.user.is_superuser and user_school:
        schools = School.objects.filter(id=user_school.id)
        classes = Class.objects.filter(school=user_school)
    else:
        schools = School.objects.all()
        classes = Class.objects.filter(school_id=school_id) if school_id else Class.objects.all()

    # Fetch routes with student counts, filtered by school
    routes_qs = Route.objects.all()
    if school_id:
        routes_qs = routes_qs.filter(school_id=school_id)
        
    routes = routes_qs.annotate(student_count=Count('assignments', filter=Q(assignments__academic_year=active_year, assignments__term=active_term, assignments__is_active=True)))

    return render(request, 'transport/dashboard.html', {
        'routes': routes,
        'vehicles': Vehicle.objects.annotate(student_count=Count('assignments', filter=Q(assignments__academic_year=active_year, assignments__term=active_term, assignments__is_active=True))),
        'students': students,
        'dropdown_students': dropdown_students,
        'total_routes': routes.count(),
        'total_vehicles': Vehicle.objects.count(),
        'total_assigned': total_assigned,
        'students_without_transport': [s for s in students if not s.active_transport],
        'schools': schools,
        'classes': classes,
        'selected_school': int(school_id) if school_id else None,
        'selected_class': int(class_id) if class_id else None,
        'can_change_school': can_change_school,
        'active_year': active_year,
        'active_term': active_term,
        'today': timezone.now().date(),
    })

@login_required
def add_route(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        ow_fee = request.POST.get('one_way_fee', 0)
        rt_fee = request.POST.get('round_trip_fee', 0)
        school_id = request.user.school.id if request.user.school else request.POST.get('school')
        
        if not school_id:
            # Fallback to Excel Academy if somehow missing
            from core.models import School
            excel = School.objects.filter(name='Excel Academy').first()
            school_id = excel.id if excel else None

        Route.objects.create(
            name=name, 
            description=description, 
            one_way_fee=ow_fee, 
            round_trip_fee=rt_fee,
            school_id=school_id
        )
        messages.success(request, f"Route '{name}' added successfully.")
        from core.activity_log import log_activity
        log_activity(request.user, 'Added Route', 'Transport', f"Added transport route '{name}'", 'Route')
    return redirect('transport:dashboard')

@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        route.name = request.POST.get('name')
        route.description = request.POST.get('description')
        route.one_way_fee = request.POST.get('one_way_fee', 0)
        route.round_trip_fee = request.POST.get('round_trip_fee', 0)
        route.save()
        messages.success(request, f"Route '{route.name}' updated successfully.")
        from core.activity_log import log_activity
        log_activity(request.user, 'Updated Route', 'Transport', f"Updated transport route '{route.name}'", 'Route', route.id)
    return redirect('transport:dashboard')

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        plate = request.POST.get('plate_number')
        model = request.POST.get('model')
        capacity = request.POST.get('capacity')
        driver = request.POST.get('driver_name')
        phone = request.POST.get('driver_phone')
        
        Vehicle.objects.create(plate_number=plate, model=model, capacity=capacity, driver_name=driver, driver_phone=phone)
        messages.success(request, f"Vehicle '{plate}' added successfully.")
        from core.activity_log import log_activity
        log_activity(request.user, 'Added Vehicle', 'Transport', f"Added vehicle '{plate}'", 'Vehicle')
    return redirect('transport:dashboard')

@login_required
def assign_transport(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        route_id = request.POST.get('route_id')
        vehicle_id = request.POST.get('vehicle_id')
        trip_type = request.POST.get('trip_type', 'round_trip')
        pickup = request.POST.get('pickup_point')
        custom_fee = request.POST.get('custom_fee')
        
        student = get_object_or_404(Student, id=student_id)
        route = get_object_or_404(Route, id=route_id)
        vehicle = get_object_or_404(Vehicle, id=vehicle_id) if vehicle_id else None
        
        active_year = AcademicYear.objects.filter(is_active=True).first()
        active_term = Term.objects.filter(is_active=True).first()

        # By using update_or_create with these specific lookup fields, 
        # we can modify an existing assignment for the same period
        # or create a new one if it doesn't exist.
        assignment, created = TransportAssignment.objects.update_or_create(
            student=student,
            academic_year=active_year,
            term=active_term,
            is_active=True,
            defaults={
                'route': route,
                'vehicle': vehicle,
                'trip_type': trip_type,
                'pickup_point': pickup,
                'custom_fee': custom_fee if custom_fee else None,
                'end_date': request.POST.get('end_date') or (active_term.closing_date if active_term else None),
            }
        )
        
        if created:
            messages.success(request, f"Transport assigned for {student.first_name}.")
            from core.activity_log import log_activity
            log_activity(request.user, 'Assigned Transport', 'Transport', f"Assigned transport to {student.get_full_name()} for route {route.name}", 'TransportAssignment', assignment.id)
        else:
            messages.success(request, f"Transport updated for {student.first_name}.")
            from core.activity_log import log_activity
            log_activity(request.user, 'Updated Transport', 'Transport', f"Updated transport for {student.get_full_name()}", 'TransportAssignment', assignment.id)
            
    # Preserve filters in redirect
    school_id = request.GET.get('school', '')
    class_id = request.GET.get('class', '')
    redirect_url = '/transport/'
    params = []
    if school_id: params.append(f"school={school_id}")
    if class_id: params.append(f"class={class_id}")
    if params: redirect_url += "?" + "&".join(params)
    
    return redirect(redirect_url)

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(TransportAssignment, id=assignment_id)
    student_name = assignment.student.get_full_name()
    assignment.delete()
    messages.success(request, f"Transport assignment for {student_name} removed.")
    from core.activity_log import log_activity
    log_activity(request.user, 'Removed Transport', 'Transport', f"Removed transport assignment for {student_name}", 'TransportAssignment')
    return redirect('transport:dashboard')
