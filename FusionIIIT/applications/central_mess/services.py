from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from datetime import timedelta
from threading import Thread
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.generic import View
from django.db.models import F, Q
from django.contrib.auth.models import User
from applications.academic_information.models import Student
from applications.globals.models import ExtraInfo, HoldsDesignation, Designation
from django.shortcuts import get_object_or_404
from .models import (Announcement, Feedback, Menu, MenuPoll, MenuPollVote, VacationSurvey, VacationSurveyResponse, Menu_change_request, Mess_meeting,
                     Mess_minutes, Mess_reg, Messinfo, Monthly_bill, Update_Payment,
                      Payments, Rebate,Special_request, Vacation_food, MessBillBase,Registration_Request, Reg_main, Reg_records ,Deregistration_Request, Semdates)
from notification.views import central_mess_notif
from .selectors import get_student_from_request_user


today_g = datetime.today()
year_g = today_g.year
tomorrow_g = today_g + timedelta(days=1)
first_day_of_this_month = date.today().replace(day=1)
this_month = first_day_of_this_month.strftime('%B')
this_year = first_day_of_this_month.year
last_day_prev_month = first_day_of_this_month - timedelta(days=1)
previous_month = last_day_prev_month.strftime('%B')
previous_month_year = last_day_prev_month.year
first_day_of_next_month = (date.today().replace(day=28) + timedelta(days=4)).replace(day=1)
last_day_of_this_month = first_day_of_next_month - timedelta(days=1)
next_month = first_day_of_next_month.month
first_day_prev_month = last_day_prev_month.replace(day=1)

def current_month():
    return date.today().strftime("%B")


def current_year():
    return date.today().strftime("%Y")

# def add_nonveg_order(request, student):
#     """
#     This function is to place non veg orders
#     :param request:
#         user: Current user
#         order_interval: Time of the day for which order is placed eg breakfast/lunch/dinner
#     :param student: student placing the order
#     :variables:
#         extra_info: Extra information about the current user. From model ExtraInfo
#         student: Student information about the current user
#         student_mess: Mess choices of the student
#         dish_request: Predefined dish available
#         nonveg_object: Object of Nonveg_data
#     :return:
#     """
#     try:
#         dish_request = Nonveg_menu.objects.get(dish=request.POST.get("dish"))
#         order_interval = request.POST.get("interval")
#         order_date = tomorrow_g
#         nonveg_object = Nonveg_data(student_id=student, order_date=order_date,
#                                     order_interval=order_interval, dish=dish_request)
#         nonveg_object.save()
#         # messages.success(request, 'Your request is forwarded !!', extra_tags='successmsg')

#     except ObjectDoesNotExist:
#         return HttpResponse("Seems like object does not exist")


def add_mess_feedback(request, student):
    """
    This function is to record the feedback submitted
    :param request:
        description: Description of feedback
        feedback_type: Type of feedback
    :param student: Student placing the request
    :variable:
         extra_info: Extra information of the user
         date_today: Today's date
         feedback_object: Object of Feedback to store current variables
    :return:
        data: to record success or any errors
    """
    date_today = datetime.now().date()
    mess_optn = Reg_main.objects.get(student_id=student)
    description = request.POST.get('description')
    feedback_type = request.POST.get('feedback_type')
    feedback_object = Feedback(student_id=student, fdate=date_today,
                               mess=mess_optn.mess_option,
                               description=description,
                               feedback_type=feedback_type)

    feedback_object.save()
    data = {
        'status': 1
    }
    return data


def add_vacation_food_request(request, student):
    """
        This function is to record vacation food requests
        :param request:
            start_date: Starting date of food request
            end_date: Last date of food request
            purpose: purpose for vacation food
        :param student: Student placing the order
        :variables:
            date_today: to record the date of the application
            vacation_object: to store current values for object of 'Vacation_food'
        :return:
            data: status = 1 or 2
    """

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    purpose = request.POST.get('purpose')
    date_today = str(datetime.now().date())
    # TODO add helper to validate the dates on order to replace the if thing from repeating
    if (start_date < date_today) or (end_date < start_date):
        data = {
            'status': 2
        }
        return data

    vacation_check = Vacation_food.objects.filter(student_id=student).prefetch_related('student_id','student_id__id','student_id__id__user','student_id__id__department')

    date_format = "%Y-%m-%d"
    b = datetime.strptime(str(start_date), date_format)
    d = datetime.strptime(str(end_date), date_format)

    for r in vacation_check:
        a = datetime.strptime(str(r.start_date), date_format)
        c = datetime.strptime(str(r.end_date), date_format)
        if ((b <= a and (d >= a and d <= c)) or (b >= a and (d >= a and d <= c))
                or (b <= a and (d >= c)) or ((b >= a and b <= c) and (d >= c))):
            flag = 0
            data = {
                'status': 3,
                'message': "Already applied for these dates",
            }
            return data

    vacation_object = Vacation_food(student_id=student, start_date=start_date,
                                    end_date=end_date, purpose=purpose)
    vacation_object.save()
    data = {
        'status': 1
    }
    return data


def add_menu_change_request(request, student):
    # TODO logic here is flawed if the same dish is use more than once then it will give an error !!!
    #  or if there are two requests on the same dish
    """
    This function is to record mess menu change requests
    :param request:
        dish: Current dish
        new_dish: Dish to be replaced
    :return:
    """
    try:

        dishID =request.POST['dish'];
        dish=Menu.objects.get(id=dishID)
        new_dish = request.POST.get("newdish")
        reason = request.POST.get("reason")
        # menu_object = Menu_change_request(dish=dish, request=new_dish, reason=reason)
        menu_object = Menu_change_request(dish=dish, student_id=student, request=new_dish, reason=reason)
        menu_object.save()
        data = {
            'status': 1
        }
        return data
    except ObjectDoesNotExist as e: 
        data = {
            'status': 0
        }
        return data


def handle_menu_change_response(request):
    # TODO logic here is flawed if the same dish is use more than once then it will give an error !!!
    #  or if there are two requests on the same dish
    """
        This function is to respond to mess menu requests
        :param request:
            stat: Accept or reject a request
            ap_id: id of the application being accepted or rejected
        :variable application: Object of Menu_change_request

        :return: data with status of the application
            5 for error
    """
    ap_id = request.POST.get('idm')
    user = request.user
    stat = request.POST['status']
    application = Menu_change_request.objects.get(id=ap_id)
    # student = application.student_id
    # receiver = User.objects.get(username=student)
    if stat == '2':
        application.status = 2
        obj = Menu.objects.get(Q(meal_time=application.dish.meal_time) & Q(mess_option=application.dish.mess_option))
        obj.dish = application.request
        obj.save()
        data = {    
            'status': '2',
        }
        # central_mess_notif(user, receiver, 'menu_change_accepted')

    elif stat == '0':
        application.status = 0
        data = {
            'status': '1',
        }

    else:
        application.status = 1
        data = {
            'status': '0',
        }

    application.save()
    # data = {
    #     'status': 1
    # }
    return data


def handle_vacation_food_request(request, ap_id):
    """
       This function records the response to vacation food requests
       :param request:
           user: Current user

       :param ap_id:

       :variables:
           holds_designations: Designation of the current user
           applications: Object of application with the given id
       :return:
    """

    applications = Vacation_food.objects.get(pk=ap_id)
    student = applications.student_id.id.user
    if request.POST.get('submit') == 'approve':
        applications.status = '2'
        central_mess_notif(request.user, student, 'vacation_request', ' accepted')

    elif request.POST.get('submit') == 'reject':
        applications.status = '0'
        central_mess_notif(request.user, student, 'vacation_request', ' rejected')

    else:
        applications.status = '1'
    applications.save()
    data = {
        'status': 1
    }
    return data


def add_mess_registration_time(request):
    """
           This function is to start mess registration
           @request:
               user: Current user
               sem: Semester for which registration is started
               start_reg: Start Date
               end_reg: End Date
               holds_designations: designation of current user to validate proper platform
               mess_reg_obj: Object of Mess_reg to store current values
           @variables:
           :return data: Status of the application
    """
    sem = request.POST['sem']
    start_reg = request.POST['start_date']
    end_reg = request.POST['end_date']
    date_today = str(today_g.date())
    if start_reg > end_reg or start_reg < date_today:
        data = {
            'status': 2,
            'message': "Please Check the Dates",
        }
        return data
    else:
        mess_reg_obj = Mess_reg(sem=sem, start_reg=start_reg, end_reg=end_reg)
        mess_reg_obj.save()
        data = {
            'status': 1,
            'message': "Registration Started Successfully"
        }
        return data


def add_leave_request(request, student):
    """
        This function is to record and validate leave requests
        :param student: Information of student submitting the request
        @request:
            leave_type: Type of leave
            start_date: Starting date of the leave
            end_date: Date of return
            purpose: Purpose of the leave
        @variables:
            today: Date today in string format
            rebates: Record of past leave requests of the student
            rebate_object:  Rebate object that stores current information
    """
    flag = 1
    today = str(datetime.now().date())
    # leave_doc = request.FILES['myfile']
    leave_type = request.POST.get('leave_type')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    purpose = request.POST.get('purpose')
    #  TODO VALIDATE DATE

    if (start_date < today) or (end_date < start_date):
        data = {
            'status': 3,
            'message': "Please check the dates"
        }
        return data

    date_format = "%Y-%m-%d"
    b = datetime.strptime(str(start_date), date_format)
    d = datetime.strptime(str(end_date), date_format)
    number_of_days = ( d - b ).days + 1

    if leave_type == "casual":
        if (number_of_days > 5) or (number_of_days < 3):
            data = {
                'status': 4,
                'message': "Cannot apply casual leave for more than 5 days or less than 3 days"
            }
            return data

    rebate_check = Rebate.objects.select_related('student_id','student_id__id','student_id__id__user','student_id__id__department').filter(student_id=student, status__in=['1', '2'])
    
    
    for r in rebate_check:
        a = datetime.strptime(str(r.start_date), date_format)
        c = datetime.strptime(str(r.end_date), date_format)
        if ((b <= a and (d >= a and d <= c)) or (b >= a and (d >= a and d <= c))
                or (b <= a and (d >= c)) or ((b >= a and b <= c) and (d >= c))):
            flag = 0
            data = {
                'status': 3,
                'message': "Already applied for these dates",
            }
            return data

    rebate_object = Rebate(student_id=student, leave_type=leave_type, start_date=start_date,
                           end_date=end_date, purpose=purpose)
    rebate_object.save()
    data = {
        'status': 1,
    }
    return data


def add_mess_meeting_invitation(request):
    """
       This function is to schedule a mess committee meeting
       @request:
           date: Date of the meeting
           venue: Venue of the meeting
           time: Time of the meeting
           agenda: Agenda of the meeting
       @variables:
           invitation_obj: Object of Mess_meeting with current values of date, venue, agenda, meeting time
    """
    date = request.POST['date']
    venue = request.POST['venue']
    agenda = request.POST['agenda']
    time = request.POST['time']
    members_mess = HoldsDesignation.objects.select_related().filter(Q(designation__name__contains='mess_convener')
                                                       | Q(designation__name__contains='mess_committee')|Q(designation__name='mess_manager')
                                                   | Q(designation__name='mess_warden'))
    date_today = str(today_g.date())
    if date <= date_today:
        data = {
            'status': 2,
            'message': "Cannot place invitation for a date that already passed"
        }
        return data

    invitation_obj = Mess_meeting(meet_date=date, agenda=agenda, venue=venue, meeting_time=time)
    invitation_obj.save()
    message = "Mess Committee meeting on " + date_today + " at " + time + ".\n Venue: " + venue + ".\n  Agenda: " + agenda
    for invi in members_mess:
        central_mess_notif(request.user, invi.user, 'meeting_invitation', message)

    data = {
            'status': 1,
            'message': "Meeting Details recorded",
            'date': date,
            'time': time,
    }
    return data

def rebateCountFn(start_date, end_date, student_id):
    '''
    This function is used to store the rebate_count in generte bill table and in what month that rebate has been issued.
    '''    
    start_date_month = start_date.strftime('%B')
    start_date_year = start_date.year
    end_date_month = end_date.strftime('%B')
    date_format = "%Y-%m-%d"
    begin_day = datetime.strptime(str(start_date), date_format)
    end_day = datetime.strptime(str(end_date), date_format)
    rebate_count_days = 0
    rebate_count_days_next_month = 0
    if start_date_month != end_date_month:
        last_day_day = int(last_day_of_this_month.day)
        begin_day_day = int(begin_day.day)
        end_day_day = int(end_day.day)
        first_day_day = int(first_day_of_next_month.day)
        rebate_count_days = abs(last_day_day-begin_day_day) + 1 
        rebate_count_days_next_month = abs(end_day_day-first_day_day)+1
    else:
        rebate_count_days = abs((end_day - begin_day).days) + 1
    
    #### Storing the rebate count days into the monthly bill table so it can be used while bill generation.
        
    try:
        existing_student = Monthly_bill.objects.get(student_id=student_id, month=start_date_month, year=start_date_year)
        new_rebate_count = existing_student.rebate_count + rebate_count_days
        existing_student.rebate_count = new_rebate_count
        existing_student.save()
        if(rebate_count_days_next_month != 0):
            new_student = Monthly_bill.objects.create(student_id=student_id, month=end_date_month, year=start_date_year, rebate_count=rebate_count_days_next_month)
            new_student.save()        
    except:
            new_student = Monthly_bill.objects.create(student_id=student_id, month=start_date_month, year=start_date_year, rebate_count=rebate_count_days)
            new_student.save()
            if(rebate_count_days_next_month != 0):
                new_student = Monthly_bill.objects.create(student_id=student_id, month=end_date_month, year=start_date_year, rebate_count=rebate_count_days_next_month)
                new_student.save() 
        
    
        
    
    
def handle_rebate_response(request):
    """
       This function is to respond to rebate requests
       @variables:
       id: id of the rebate request
       leaves: Object corresponding to the id of the rebate request
       @return:
       data: returns the status of the application
    """
    id = request.POST.get('id_rebate')
    leaves = Rebate.objects.get(pk=id)

    # receiver = ExtraInfo.
    date_format = "%Y-%m-%d"
    message = ''
    b = datetime.strptime(str(leaves.start_date), date_format)
    d = datetime.strptime(str(leaves.end_date), date_format)
    rebate_count = abs((d - b).days) + 1
    receiver = leaves.student_id.id.user
    action = request.POST["status"]
    remark = request.POST["remark"]
    leaves.rebate_remark = remark
    leaves.status = action
    leaves.save()
    if action == '2':
        rebateCountFn(leaves.start_date, leaves.end_date, leaves.student_id)
        message = 'Your leave request has been accepted between dates ' + str(b.date()) + ' and ' + str(d.date())
    else:
        message = 'Your leave request has been rejected between dates ' + str(b.date()) + ' and ' + str(d.date())
    central_mess_notif(request.user, receiver, 'leave_request', message)
    data = {
        'message': 'You responded to request !'
    }
    return data


def add_special_food_request(request, student):
    """
        This function is to place special food requests ( used by students )
        @variables:
        user: Current user
        student: Information regarding the student placing the request
        purpose: The purpose for the special food request *taken from "purpose" POST method
        date_today: String of today's date allows checking dates to avoid reduntant values
        spfood_obj: Special Request object to store values to be updated
        @request:
        fr: Start Date of the food request *taken from form "start_date" POST method
        to: End Date of the food request *taken from form "end_date" POST method
        food1: Food option 1 *taken from form "food1" POST method
        food2: Food option 2 *taken from form "food2" POST method
        @return:
        data['status']: returns status of the application
    """
    fr = request.POST.get("start_date")
    to = request.POST.get("end_date")
    food1 = request.POST.get("food1")
    food2 = request.POST.get("food2")
    purpose = request.POST.get('purpose')
    # date_format = "%Y-%m-%d"
    date_today = datetime.now().date()
    date_today = str(date_today)
    date_format = "%Y-%m-%d"
    b = datetime.strptime(str(fr), date_format)
    d = datetime.strptime(str(to), date_format)
    #   TODO ADD DATE VALIDATION
    if (date_today > to) or (to < fr):
        data = {
            'status': 3,
            # case when the to date has passed
        }
        # messages.error(request, "Invalid dates")
        return data
    spfood_obj = Special_request(student_id=student, start_date=fr, end_date=to,
                                 item1=food1, item2=food2, request=purpose)
    s_check = Special_request.objects.select_related('student_id','student_id__id','student_id__id__user','student_id__id__department').filter(student_id=student,status__in=['1', '2']).order_by('-app_date')


    for r in s_check:
        a = datetime.strptime(str(r.start_date), date_format)
        c = datetime.strptime(str(r.end_date), date_format)
        if ((b <= a and (d >= a and d <= c)) or (b >= a and (d >= a and d <= c))
                or (b <= a and (d >= c)) or ((b >= a and b <= c) and (d >= c))):
            flag = 0
            data = {
                'status': 2,
                'message': "Already applied for these dates",
            }
            return data
    spfood_obj.save()
    data = {
        'status': 1,
    }
    return data



def handle_special_request(request):
    """
       This function is to respond to special request for food submitted by students
       @variables:
       special_request: data corresponding to id of the special request being accepted or rejected
    """
    special_request = Special_request.objects.get(pk=request.POST["id"])
    receiver = special_request.student_id.id.user
    action = request.POST["status"]
    message = 'rejected'
    special_request.status = action
    special_request.save()
    if action == '2':
        message= "accepted"
    central_mess_notif(request.user, receiver, 'special_request', message)
    data = {
        'message': 'You responded to the request !'
    }
    return data


def add_bill_base_amount(request):
    """
    This function is to update the base cost of the monthly central mess bill
    :param request:
    :return:
    """
    # month_now = today.strftime('%B')
    cost = request.POST.get("amount")
    # if cost < 0:
    #     data = {
    #         'status' : '2',
    #         'message': "Negative Values not allowed"
    #     }
    #     return data
    data = {
        'status': 1,
        'message': "Successfully updated"
    }
    amount_object = MessBillBase(bill_amount=cost)
    amount_object.save()

    return data

def add_sem_dates(request):
    """
    This function is to update the semester start and end date
    :param request:
    :return:
    """
    start_date = request.POST.get("semstart_date")
    end_date = request.POST.get("semend_date")

    if (end_date <= start_date):
        data = {
            'status': 3,
            'message': "Please check the dates"
        }
        return data
    
    data = {
        'status': 1,
        'message': "Successfully updated"
    }
    semdate_object = Semdates(start_date=start_date, end_date=end_date)
    semdate_object.save()
    return data

def add_mess_committee(request, roll_number):
    studentHere = Student.objects.get(id=roll_number)
    try:
        mess = Messinfo.objects.get(student_id_id=studentHere)
        if mess.mess_option == 'mess1':
            designation = Designation.objects.get(name='mess_committee')
        else:
            designation = Designation.objects.get(name='mess_committee_mess2')
        check_obj=HoldsDesignation.objects.select_related().filter(Q(user__username=studentHere) &
                                                (Q(designation__name__contains='mess_committee')
                                                 | Q(designation__name__contains='mess_convener')))
        if check_obj:
            data = {
                'status': 2,
                'message': roll_number + " is already a part of mess committee"
            }
            return data
        else:
            add_user = User.objects.get(username=roll_number)
            designation_object = HoldsDesignation(user=add_user, working=add_user, designation=designation)
            designation_object.save()
            central_mess_notif(request.user, add_user, 'added_committee', '')
            data = {
                'status': 1,
                'message': roll_number + " is added to Mess Committee"
            }
        return data
    except:
        data = {
            'status': 0,
            'message': roll_number + " is not registered for any Mess."
        }


def Calculate_rebate(id, month_previous, amount_per_day):
    students = Rebate.objects.filter(student_id_id=id)
    print(students)
    no_of_days = 0
    for student in students:
        start_date_month = student.start_date.month
        end_date_month = student.end_date.month
        if(start_date_month == month_previous):
            if(end_date_month == month_previous):
                no_of_days = no_of_days + abs((student.end_date - student.start_date).days) + 1 
            elif(end_date_month == today_g.month):
                no_of_days = no_of_days + abs((last_day_prev_month - student.start_date).days) + 1 
        else:
            if(end_date_month == month_previous):
                no_of_days = no_of_days + abs((student.end_date - student.start_date).days) + 1 
            elif(end_date_month == today_g.month):
                no_of_days = no_of_days + abs((last_day_prev_month - first_day_prev_month).days) + 1
    print(no_of_days)
    rebate_amount = no_of_days*amount_per_day
    return rebate_amount
            

def generate_bill():
    
    per_day_cost_obj = MessBillBase.objects.latest('timestamp')
    per_day_cost = per_day_cost_obj.bill_amount
    print(per_day_cost)
    amount = int(last_day_prev_month.day) * int(per_day_cost)
    print(amount)
    student_all = Reg_main.objects.filter(current_mess_status = "Registered")
    print(student_all)
    for student in student_all:
        student_id = student.student_id
        rem_balance = student.balance
        try:        
            monthly_bill_obj = Monthly_bill.objects.get(student_id=student_id, month=previous_month, year=previous_month_year)
            rebate_count_count = monthly_bill_obj.rebate_count
            rebate_amount = int(rebate_count_count)*int(per_day_cost)
            monthly_bill_obj.rebate_amount = rebate_amount
            total_bill = amount - rebate_amount
            monthly_bill_obj.total_bill = total_bill
            rem_balance = rem_balance - total_bill
            student.balance = rem_balance
            monthly_bill_obj.amount = amount
            monthly_bill_obj.save()
        except:
            new_monthly_bill_obj = Monthly_bill(student_id=student_id, month=previous_month, year=previous_month_year, amount=amount, total_bill=amount)
            rem_balance = rem_balance - amount
            student.balance = rem_balance
            new_monthly_bill_obj.save()
        if(student.balance <= 0):
            student.current_mess_status = 'Deregistered'
        student.save()
        



def handle_reg_response(request):
    """
       This function is to respond to registeration requests
       @variables:
       id: id of the registeration request
       reg_req: Object corresponding to the id of the reg request
       @return:
       data: returns the status of the application
    """

    id = request.POST['id_reg']
    status = request.POST['status']
    remark = request.POST['remark']
    reg_req = Registration_Request.objects.get(pk=id)
    start_date = reg_req.start_date
    payment_date = reg_req.payment_date
    student = reg_req.student_id
    reg_req.status = status
    reg_req.registration_remark=remark
    try:
        sem_end_date = Semdates.objects.latest('start_date').end_date
    except:
        sem_end_date= None
    reg_req.save()
    message=''
    if(status=='accept'):
        amount = reg_req.amount
        mess = request.POST['mess_no']
        try :
            reg_main = Reg_main.objects.get(student_id=student)
            if(start_date == date.today()):
                reg_main.current_mess_status="Registered"
            else:
                reg_main.current_mess_status = "Deregistered"
            reg_main.mess_option=mess
            reg_main.balance=reg_main.balance+amount
            reg_main.save()
        except:
            program = student.programme
            if(start_date == date.today()):
                mess_status = "Registered"
            else:
                mess_status  = "Deregistered"
            new_reg = Reg_main(student_id=student,program=program,current_mess_status=mess_status,balance=amount,mess_option=mess)
            new_reg.save()
        new_reg_record = Reg_records(student_id=student, start_date=start_date, end_date=sem_end_date)
        new_reg_record.save()
       
        new_payment_record = Payments(student_id = student, amount_paid = amount, payment_date=payment_date, payment_month=current_month(), payment_year=current_year())
        new_payment_record.save()
        message="Your registeration request has been accepted"
    else:
        message="Your registeration request has been rejected"            
            


    
    receiver = reg_req.student_id.id.user
    central_mess_notif(request.user, receiver, 'leave_request', message)
    data = {
        'message': 'success'
    }
    return data


def handle_update_payment_response(request):
    id = request.POST['id_reg']
    status = request.POST['status']
    remark = request.POST['remark']
    payment_req = Update_Payment.objects.get(pk=id)
    payment_date = payment_req.payment_date
    student = payment_req.student_id
    payment_req.status = status
    payment_req.update_remark=remark
    
    payment_req.save()
    
    if(status == 'accept'):
        amount = payment_req.amount
        reg_main_obj= Reg_main.objects.get(student_id=student)
        new_balance = reg_main_obj.balance + amount
        reg_main_obj.balance = new_balance
        reg_main_obj.save()
        new_payment_record = Payments(student_id=student, amount_paid = amount, payment_date=payment_date, payment_month=current_month(), payment_year= current_year())
        new_payment_record.save()
        
        message = 'Your update payment request has been accepted.'
        
    else:
        message = 'Your update payment request has been rejected.'    
    
    receiver = payment_req.student_id.id.user
    central_mess_notif(request.user, receiver, 'leave_request', message)
    data = {
        'message': 'success'
    }
    return data
    

def handle_dreg_response(request):
    """
       This function is to respond to de registeration requests
       @variables:
       id: id of the registeration request
       dreg_req: Object corresponding to the id of the de reg request
       @return:
       data: returns the status of the application
    """

    id = request.POST['id_reg']
    status = request.POST['status']
    remark = request.POST['remark']
    dreg_req = Deregistration_Request.objects.get(pk=id)
    end_date = dreg_req.end_date
    student = dreg_req.student_id
    dreg_req.status = status
    dreg_req.deregistration_remark=remark
    dreg_req.save()
    message=''
    if(status=='accept'):
        try :
            reg_main = Reg_main.objects.get(student_id=student)
            if(end_date == date.today()):
                reg_main.current_mess_status="Deregistered"
            reg_record_obj = Reg_records.objects.filter(student_id = student).latest('start_date')
            reg_record_obj.end_date = end_date
            reg_record_obj.save()
            reg_main.save()
        except:
            data = {'message': 'Student does not exist in database'}
            return data
        
        message="Your De-registeration request has been accepted"
    else:
        message="Your De-registeration request has been rejected"            
            
    receiver = dreg_req.student_id.id.user
    central_mess_notif(request.user, receiver, 'leave_request', message)
    data = {
        'message': 'success'
    }
    return data

def update_month_bill(request):
    """
        This function is used to update the monthly bill of student by caretaker if any discrepancy arises. 
    """
    student = str(request.POST.get("rollNo")).upper()
    studentHere = Student.objects.get(id = student)
    new_amount = int(request.POST.get("new_amount"))
    month = request.POST.get("Month")
    year = int(request.POST.get("Year"))
    try:
        bill_base_amount = int(MessBillBase.objects.latest('timestamp').bill_amount)
    except:
        bill_base_amount = 150
    fixed_amount_per_month = int(bill_base_amount)*int(30)

    reg_main_obj = Reg_main.objects.get(student_id=student)
    curr_balance = reg_main_obj.balance
    try:
        existing_monthly_bill_object = Monthly_bill.objects.get(student_id = studentHere, month=month, year=year)
        previous_total_bill = existing_monthly_bill_object.total_bill
        curr_balance = curr_balance + previous_total_bill
        existing_monthly_bill_object.total_bill = new_amount
        curr_balance = curr_balance - int(new_amount)
        reg_main_obj.balance = curr_balance
        reg_main_obj.save() 
        existing_monthly_bill_object.save()
    except:
        new_monthly_bill_obj = Monthly_bill(student_id = studentHere, month=month, year= year, total_bill = new_amount, amount=fixed_amount_per_month)
        curr_balance = curr_balance - new_amount
        reg_main_obj.balance = curr_balance
        reg_main_obj.save()
        new_monthly_bill_obj.save()
    data = {
        'message': 'success'
    }
    return data

def handle_add_reg(request):
    start_date = request.POST['start_date']
    amount = int(request.POST['amount'])
    studentID = str(request.POST['input_roll']).upper()
    student = Student.objects.select_related('id','id__user','id__department').get(id=studentID)
    payment_date = request.POST['payment_date']
    try:
        latest=Semdates.objects.latest('start_date')
        latest_end_date = latest.end_date
    except:
        latest_end_date= None
    
    mess=request.POST['mess_option_form']
    try :
        reg_main = Reg_main.objects.get(student_id=studentID)
        if(start_date==str(date.today())):
            reg_main.current_mess_status='Registered'
        reg_main.mess_option=mess
        reg_main.balance=reg_main.balance+amount
        reg_main.save()
    except:
        program = student.programme
        if(start_date==str(date.today())):
            mess_status = "Registered"
        else:
            mess_status = "Deregistered"
        new_reg = Reg_main(student_id=student,program=program,current_mess_status=mess_status,balance=amount,mess_option=mess)
        new_reg.save()

    new_reg_record = Reg_records(student_id=student, start_date=start_date,end_date = latest_end_date)
    new_reg_record.save()
   
    new_payment_record = Payments(student_id = student, amount_paid = amount, payment_date=payment_date, payment_month=current_month(), payment_year=current_year())
    new_payment_record.save()
    message="Your registeration request has been accepted"


class CentralMessServiceError(Exception):
    """Base service-level exception for central mess API flows."""

    def __init__(self, message, *, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class RebateOverlapError(CentralMessServiceError):
    pass


def _get_student(validated_data, request_user=None):
    student = validated_data.get("student_id")
    if student is not None:
        return student
    if request_user is not None:
        return get_student_from_request_user(request_user)
    raise CentralMessServiceError("student_id is required.")


def _normalize_status(status):
    return str(status).strip().lower()


def create_feedback(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)
    if not payload.get("mess"):
        reg_main = Reg_main.objects.filter(student_id=payload["student_id"]).first()
        if reg_main:
            payload["mess"] = reg_main.mess_option

    # BR-009: Only one feedback allowed per day per student
    feedback_date = payload.get("fdate", date.today())
    if Feedback.objects.filter(student_id=payload["student_id"], fdate=feedback_date).exists():
        raise CentralMessServiceError(
            "You have already submitted feedback today. Only one feedback per day is allowed.",
            status_code=400,
        )

    return Feedback.objects.create(**payload)


def update_feedback_status(validated_data):
    feedback = get_object_or_404(
        Feedback,
        student_id=validated_data["student_id"],
        mess=validated_data["mess"],
        feedback_type=validated_data["feedback_type"],
        description=validated_data["description"],
        fdate=validated_data["fdate"],
    )
    feedback.feedback_remark = validated_data.get("feedback_remark", feedback.feedback_remark)
    feedback.save(update_fields=["feedback_remark"])
    return feedback


def create_messinfo(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)
    return Messinfo.objects.create(**payload)


def create_mess_reg(validated_data):
    return Mess_reg.objects.create(**validated_data)


def create_mess_bill_base(validated_data):
    return MessBillBase.objects.create(**validated_data)


def create_menu(validated_data):
    return Menu.objects.create(**validated_data)


def update_menu_items(mess_option, items):
    """Bulk update-or-create menu items for a given mess."""
    for item in items:
        Menu.objects.update_or_create(
            mess_option=mess_option,
            meal_time=item['meal_time'],
            defaults={'dish': item['dish']},
        )


def create_monthly_bill(validated_data):
    payload = dict(validated_data)
    amount = payload.get("amount", 0)
    rebate_count = payload.get("rebate_count", 0)
    rebate_amount = payload.get("rebate_amount", 0)
    total_bill = amount - (rebate_count * rebate_amount)

    obj, _ = Monthly_bill.objects.update_or_create(
        student_id=payload["student_id"],
        month=payload["month"],
        year=payload["year"],
        defaults={
            "amount": amount,
            "rebate_count": rebate_count,
            "rebate_amount": rebate_amount,
            "total_bill": total_bill,
            "paid": payload.get("paid", False),
        },
    )
    return obj


def create_rebate(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)

    start_date = payload["start_date"]
    end_date = payload["end_date"]

    # BR-004: Rebate start date must be in the future
    if start_date <= date.today():
        raise CentralMessServiceError(
            "Rebate start date must be a future date.",
            status_code=400,
            payload={"status": 3, "message": "Rebate start date must be a future date."},
        )

    overlapping = Rebate.objects.filter(
        student_id=payload["student_id"],
        status="2",
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if overlapping.exists():
        raise RebateOverlapError(
            "Already applied for these dates",
            payload={"status": 3, "message": "Already applied for these dates"},
        )

    # BR-012: Maximum 20 rebate days per semester
    today = date.today()
    sem = Semdates.objects.filter(start_date__lte=today, end_date__gte=today).first()
    if sem:
        existing = Rebate.objects.filter(
            student_id=payload["student_id"],
            status__in=["1", "2"],
            start_date__gte=sem.start_date,
            end_date__lte=sem.end_date,
        )
        used_days = sum((r.end_date - r.start_date).days + 1 for r in existing)
        new_days = (end_date - start_date).days + 1
        if used_days + new_days > 20:
            raise CentralMessServiceError(
                f"Maximum 20 rebate days allowed per semester. You have used {used_days} days.",
                status_code=400,
                payload={"status": 3, "message": f"Maximum 20 rebate days allowed per semester. Used: {used_days}/20."},
            )

    return Rebate.objects.create(**payload)


def update_rebate_status(validated_data):
    rebate = get_object_or_404(
        Rebate,
        student_id=validated_data["student_id"],
        start_date=validated_data["start_date"],
        end_date=validated_data["end_date"],
        purpose=validated_data["purpose"],
        app_date=validated_data["app_date"],
        leave_type=validated_data["leave_type"],
    )
    rebate.status = validated_data["status"]
    rebate.rebate_remark = validated_data.get("rebate_remark", rebate.rebate_remark)
    rebate.save(update_fields=["status", "rebate_remark"])
    return rebate


def create_vacation_food(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)
    return Vacation_food.objects.create(**payload)


def update_vacation_food_status(validated_data):
    request_obj = (
        Vacation_food.objects.filter(
            student_id=validated_data["student_id"],
            app_date=validated_data["app_date"],
            purpose=validated_data["purpose"],
            end_date=validated_data["end_date"],
            start_date=validated_data["start_date"],
        )
        .order_by("-app_date")
        .first()
    )
    if request_obj is None:
        raise CentralMessServiceError("Vacation food request not found.", status_code=404)

    request_obj.status = validated_data["status"]
    request_obj.save(update_fields=["status"])
    return request_obj


def create_special_request(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)

    # BR-013: Maximum 3 special food requests per semester
    today = date.today()
    sem = Semdates.objects.filter(start_date__lte=today, end_date__gte=today).first()
    if sem:
        existing_count = Special_request.objects.filter(
            student_id=payload["student_id"],
            status__in=["1", "2"],
            app_date__gte=sem.start_date,
            app_date__lte=sem.end_date,
        ).count()
        if existing_count >= 3:
            raise CentralMessServiceError(
                "Maximum 3 special food requests allowed per semester.",
                status_code=400,
            )

    return Special_request.objects.create(**payload)


def update_special_request_status(validated_data):
    request_obj = get_object_or_404(
        Special_request,
        student_id=validated_data["student_id"],
        app_date=validated_data["app_date"],
        item1=validated_data["item1"],
        item2=validated_data["item2"],
        end_date=validated_data["end_date"],
        start_date=validated_data["start_date"],
        request=validated_data["request"],
    )
    request_obj.status = validated_data["status"]
    request_obj.save(update_fields=["status"])
    return request_obj


def create_registration_request(validated_data, *, request_user):
    payload = dict(validated_data)
    payload.pop("mess_option", None)
    student = _get_student(payload, request_user=request_user)

    reg_main = Reg_main.objects.filter(student_id=student).first()
    if reg_main and str(reg_main.current_mess_status).lower() == "registered":
        raise CentralMessServiceError(
            "You are already registered in mess. Deregister first before applying again.",
            status_code=400,
        )

    pending_registration_exists = Registration_Request.objects.filter(
        student_id=student,
        status__iexact="pending",
    ).exists()
    if pending_registration_exists:
        raise CentralMessServiceError(
            "A registration request is already pending. Please wait until it is rejected or processed.",
            status_code=400,
        )

    payload["student_id"] = student
    return Registration_Request.objects.create(**payload)


@transaction.atomic
def decide_registration_request(validated_data):
    request_obj = get_object_or_404(
        Registration_Request,
        student_id=validated_data["student_id"],
        start_date=validated_data["start_date"],
        payment_date=validated_data["payment_date"],
        amount=validated_data["amount"],
        Txn_no=validated_data["Txn_no"],
    )

    new_status = _normalize_status(validated_data["status"])
    old_status = _normalize_status(request_obj.status)

    request_obj.status = new_status
    request_obj.registration_remark = validated_data.get(
        "registration_remark", request_obj.registration_remark
    )
    request_obj.save(update_fields=["status", "registration_remark"])

    if new_status == "accept" and old_status != "accept":
        student = request_obj.student_id
        amount = request_obj.amount
        mess_option = validated_data.get("mess_option", "mess2")

        Payments.objects.create(
            student_id=student,
            amount_paid=amount,
            payment_date=request_obj.payment_date,
            payment_month=current_month(),
            payment_year=current_year(),
        )

        reg_main, created = Reg_main.objects.get_or_create(
            student_id=student,
            defaults={
                "program": student.programme,
                "current_mess_status": "Registered",
                "balance": amount,
                "mess_option": mess_option,
            },
        )
        if not created:
            reg_main.current_mess_status = "Registered"
            reg_main.balance = F("balance") + amount
            reg_main.mess_option = mess_option
            reg_main.save(update_fields=["current_mess_status", "balance", "mess_option"])

        Reg_records.objects.create(
            student_id=student,
            start_date=request_obj.start_date,
            end_date=None,
        )

    return request_obj


def create_deregistration_request(validated_data, *, request_user):
    payload = dict(validated_data)
    student = _get_student(payload, request_user=request_user)

    reg_main = Reg_main.objects.filter(student_id=student).first()
    if not reg_main or str(reg_main.current_mess_status).lower() != "registered":
        raise CentralMessServiceError(
            "Only registered students can apply for deregistration.",
            status_code=400,
        )

    pending_deregistration_exists = Deregistration_Request.objects.filter(
        student_id=student,
        status__iexact="pending",
    ).exists()
    if pending_deregistration_exists:
        raise CentralMessServiceError(
            "A deregistration request is already pending. You can apply again only if it is rejected.",
            status_code=400,
        )

    payload["student_id"] = student
    return Deregistration_Request.objects.create(**payload)


def delete_deregistration_request(validated_data, *, request_user):
    request_id = validated_data["id"]
    request_obj = get_object_or_404(Deregistration_Request, id=request_id)

    requester_student = get_student_from_request_user(request_user)
    if request_obj.student_id != requester_student:
        raise CentralMessServiceError(
            "You can delete only your own deregistration request.",
            status_code=403,
        )

    if _normalize_status(request_obj.status) != "pending":
        raise CentralMessServiceError(
            "Only pending deregistration requests can be deleted.",
            status_code=400,
        )

    request_obj.delete()
    return True


@transaction.atomic
def decide_deregistration_request(validated_data):
    request_obj = get_object_or_404(
        Deregistration_Request,
        student_id=validated_data["student_id"],
        end_date=validated_data["end_date"],
    )

    new_status = _normalize_status(validated_data["status"])
    old_status = _normalize_status(request_obj.status)

    request_obj.status = new_status
    request_obj.deregistration_remark = validated_data.get(
        "deregistration_remark", request_obj.deregistration_remark
    )
    request_obj.save(update_fields=["status", "deregistration_remark"])

    if new_status == "accept" and old_status != "accept":
        reg_main = get_object_or_404(Reg_main, student_id=request_obj.student_id)
        reg_main.current_mess_status = "Deregistered"
        reg_main.save(update_fields=["current_mess_status"])

        reg_record = (
            Reg_records.objects.filter(student_id=request_obj.student_id)
            .order_by("-start_date")
            .first()
        )
        if reg_record:
            reg_record.end_date = request_obj.end_date
            reg_record.save(update_fields=["end_date"])

    return request_obj


def create_update_payment_request(validated_data, *, request_user):
    payload = dict(validated_data)
    payload["student_id"] = _get_student(payload, request_user=request_user)
    return Update_Payment.objects.create(**payload)


@transaction.atomic
def decide_update_payment_request(validated_data):
    request_obj = get_object_or_404(
        Update_Payment,
        student_id=validated_data["student_id"],
        payment_date=validated_data["payment_date"],
        amount=validated_data["amount"],
        Txn_no=validated_data["Txn_no"],
    )

    new_status = _normalize_status(validated_data["status"])
    old_status = _normalize_status(request_obj.status)

    request_obj.status = new_status
    request_obj.update_remark = validated_data.get(
        "update_payment_remark", request_obj.update_remark
    )
    request_obj.save(update_fields=["status", "update_remark"])

    if new_status == "accept" and old_status != "accept":
        student = request_obj.student_id
        amount = request_obj.amount

        Payments.objects.create(
            student_id=student,
            amount_paid=amount,
            payment_date=request_obj.payment_date,
            payment_month=current_month(),
            payment_year=current_year(),
        )

        reg_main = get_object_or_404(Reg_main, student_id=student)
        reg_main.balance = F("balance") + amount
        reg_main.save(update_fields=["balance"])

    return request_obj


# ---------------------------------------------------------------------------
# Mess Meeting & Minutes
# ---------------------------------------------------------------------------

def create_mess_meeting(validated_data):
    return Mess_meeting.objects.create(**validated_data)


def create_mess_minutes(validated_data):
    return Mess_minutes.objects.create(**validated_data)


# ---------------------------------------------------------------------------
# Menu Change Request
# ---------------------------------------------------------------------------

def create_menu_change_request(data, *, request_user):
    """Create a menu change request from raw request data."""
    dish_obj = get_object_or_404(Menu, dish=data["dish"])
    info = get_object_or_404(ExtraInfo, user=request_user)
    student = get_object_or_404(Student, id=info.id)
    return Menu_change_request.objects.create(
        student_id=student,
        app_date=data.get("app_date"),
        status=data.get("status", "1"),
        reason=data.get("reason", ""),
        request=data.get("request", ""),
        dish=dish_obj,
    )


# ---------------------------------------------------------------------------
# Feedback delete
# ---------------------------------------------------------------------------

def delete_feedback(data):
    feedback = get_object_or_404(
        Feedback,
        student_id=data.get("student_id"),
        mess=data.get("mess"),
        feedback_type=data.get("feedback_type"),
        description=data.get("description"),
        fdate=data.get("fdate"),
    )
    feedback.delete()


# ---------------------------------------------------------------------------
# Excel bill update
# ---------------------------------------------------------------------------

@transaction.atomic
def process_excel_bill_update(file):
    """Parse an .xlsx / .xls file and bulk-update monthly bills and balances."""
    from openpyxl import load_workbook

    wb = load_workbook(file)
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2):
        student_id = str(row[0].value).upper()
        try:
            student = Student.objects.select_related(
                "id", "id__user", "id__department"
            ).get(id=student_id)
        except Student.DoesNotExist:
            continue

        month = str(row[1].value)
        year = row[2].value
        amt = row[3].value
        rebate_cnt = row[4].value
        rebate_amt = row[5].value
        total_amt = row[6].value

        try:
            bill = Monthly_bill.objects.get(
                student_id=student_id, month=month, year=year
            )
            reg_main = Reg_main.objects.get(student_id=student_id)
            reg_main.balance += bill.total_bill
            bill.amount = amt
            bill.rebate_count = rebate_cnt
            bill.rebate_amount = rebate_amt
            bill.total_bill = total_amt
            reg_main.balance -= total_amt
            bill.save()
            reg_main.save()
        except Monthly_bill.DoesNotExist:
            Monthly_bill.objects.create(
                student_id=student,
                month=month,
                year=year,
                amount=amt,
                rebate_count=rebate_cnt,
                rebate_amount=rebate_amt,
                total_bill=total_amt,
            )


@transaction.atomic
def admin_register_student(student_id_str, mess_option, amount, program, request_user):
    """Directly register a student to a mess (admin action, bypasses request flow)."""
    from applications.academic_information.models import Student
    try:
        student = Student.objects.get(id__user__username=student_id_str.upper())
    except Student.DoesNotExist:
        try:
            student = Student.objects.get(id__id=student_id_str.upper())
        except Student.DoesNotExist:
            raise CentralMessServiceError(f"Student '{student_id_str}' not found.", status_code=404)

    reg_main, created = Reg_main.objects.get_or_create(
        student_id=student,
        defaults={"program": program or "UG", "mess_option": mess_option, "balance": amount},
    )
    if not created:
        reg_main.current_mess_status = "Registered"
        reg_main.mess_option = mess_option
        reg_main.balance = F("balance") + amount
        reg_main.save(update_fields=["current_mess_status", "mess_option", "balance"])
    else:
        reg_main.current_mess_status = "Registered"
        reg_main.save(update_fields=["current_mess_status"])

    Reg_records.objects.create(student_id=student, start_date=date.today())
    return reg_main


@transaction.atomic
def admin_deregister_student(student_id_str, request_user):
    """Directly deregister a student from mess (admin action)."""
    from applications.academic_information.models import Student
    try:
        student = Student.objects.get(id__user__username=student_id_str.upper())
    except Student.DoesNotExist:
        try:
            student = Student.objects.get(id__id=student_id_str.upper())
        except Student.DoesNotExist:
            raise CentralMessServiceError(f"Student '{student_id_str}' not found.", status_code=404)

    reg_main = Reg_main.objects.filter(student_id=student).first()
    if not reg_main:
        raise CentralMessServiceError("Student is not registered in mess.", status_code=404)
    reg_main.current_mess_status = "Deregistered"
    reg_main.save(update_fields=["current_mess_status"])

    reg_record = Reg_records.objects.filter(student_id=student, end_date__isnull=True).order_by("-start_date").first()
    if reg_record:
        reg_record.end_date = date.today()
        reg_record.save(update_fields=["end_date"])
    return reg_main


@transaction.atomic
def admin_deregister_all_from_mess(mess_option, request_user):
    """Deregister all students from a given mess (admin action)."""
    students = Reg_main.objects.filter(mess_option=mess_option, current_mess_status="Registered")
    count = students.count()
    student_ids = list(students.values_list("student_id", flat=True))
    students.update(current_mess_status="Deregistered")
    Reg_records.objects.filter(
        student_id__in=student_ids, end_date__isnull=True
    ).update(end_date=date.today())
    return count


def create_menu_poll(validated_data, *, request_user):
    from applications.globals.models import ExtraInfo
    payload = dict(validated_data)
    payload.pop("created_by", None)
    if request_user is not None:
        extra_info = ExtraInfo.objects.filter(user=request_user).first()
        if extra_info:
            payload["created_by"] = extra_info
    return MenuPoll.objects.create(**payload)


def submit_poll_vote(poll_id, selected_option, *, request_user):
    poll = get_object_or_404(MenuPoll, pk=poll_id, is_active=True)
    student = _get_student({}, request_user=request_user)

    # Validate option exists on poll
    option_map = {1: poll.option1, 2: poll.option2, 3: poll.option3, 4: poll.option4}
    if not option_map.get(selected_option):
        raise CentralMessServiceError("Invalid option selected.", status_code=400)

    vote, created = MenuPollVote.objects.update_or_create(
        poll=poll,
        student_id=student,
        defaults={"selected_option": selected_option},
    )
    return vote


def close_menu_poll(poll_id, *, request_user):
    poll = get_object_or_404(MenuPoll, pk=poll_id)
    poll.is_active = False
    poll.save(update_fields=["is_active"])
    return poll


def create_vacation_survey(validated_data, *, request_user):
    from applications.globals.models import ExtraInfo
    payload = dict(validated_data)
    payload.pop("created_by", None)
    if request_user is not None:
        extra_info = ExtraInfo.objects.filter(user=request_user).first()
        if extra_info:
            payload["created_by"] = extra_info
    return VacationSurvey.objects.create(**payload)


def submit_survey_response(survey_id, response, remarks, *, request_user):
    survey = get_object_or_404(VacationSurvey, pk=survey_id, is_active=True)
    student = _get_student({}, request_user=request_user)
    valid_responses = {"staying", "leaving", "undecided"}
    if response not in valid_responses:
        raise CentralMessServiceError(f"response must be one of {valid_responses}.", status_code=400)
    obj, _ = VacationSurveyResponse.objects.update_or_create(
        survey=survey,
        student_id=student,
        defaults={"response": response, "remarks": remarks or ""},
    )
    return obj


def create_announcement(validated_data, *, request_user):
    from applications.globals.models import ExtraInfo
    payload = dict(validated_data)
    payload.pop("created_by", None)
    if request_user is not None:
        extra_info = ExtraInfo.objects.filter(user=request_user).first()
        if extra_info:
            payload["created_by"] = extra_info
    return Announcement.objects.create(**payload)


def delete_announcement(announcement_id, *, request_user):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    announcement.delete()
