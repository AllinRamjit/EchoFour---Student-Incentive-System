import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Request, Staff, LoggedHours, Accolade, Activity
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)
from App.controllers.student_controller import (
    register_student,
    create_hours_request,
    fetch_requests,
    get_approved_hours,
    fetch_accolades,
    generate_leaderboard,
    get_activity_history,
    request_confirmation_of_hours
)
from App.controllers.staff_controller import (
    register_staff,
    fetch_all_requests,
    process_request_approval,
    process_request_denial,
    confirm_hours,
    reject_hours,
    log_hours_for_student
)
from App.controllers.accolade_controller import (
    create_accolade,
    award_accolade,
    get_student_accolades
)
from App.controllers.activity_controller import (
    create_activity_log,
    update_activity_status,
    get_student_activities
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_init_user(self):
        Testuser = User(username="David Goggins", email="goggs@gmail.com", password="goggs123", role="student")
        self.assertEqual(Testuser.username, "David Goggins")   
        self.assertEqual(Testuser.role, "student")
        self.assertEqual(Testuser.email, "goggs@gmail.com") 
        self.assertTrue(Testuser.check_password("goggs123"))

    def test_user_get_json(self):
        Testuser = User(username="David Goggins", email="goggs@gmail.com", password="goggs123", role="student")
        user_json = Testuser.get_json()
        self.assertEqual(user_json['username'], "David Goggins")
        self.assertEqual(user_json['email'], "goggs@gmail.com")
        # Note: role is not in get_json() based on your User model

    def test_check_password(self):
        Testuser = User(username="David Goggins", email="goggs@gmail.com", password="goggs123", role="student")
        self.assertTrue(Testuser.check_password("goggs123"))
        self.assertFalse(Testuser.check_password("wrongpassword"))

    def test_set_password(self):
        Testuser = User(username="bob", email="bob@email.com", password="oldpass", role="user")
        new_password = "newpass"
        Testuser.set_password(new_password)
        self.assertTrue(Testuser.check_password(new_password))
        self.assertFalse(Testuser.check_password("oldpass"))

    def test_login_static_method(self):
        # This tests the static login method in User model
        user = User(username="testuser", email="test@email.com", password="testpass", role="user")
        db.session.add(user)
        db.session.commit()
        
        result = User.login("testuser", "testpass")
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        
        result = User.login("testuser", "wrongpass")
        self.assertIsNone(result)

class StaffUnitTests(unittest.TestCase):

    def test_init_staff(self):
        newstaff = Staff(username="Jacob Lester", email="jacob55@gmail.com", password="Jakey55")
        self.assertEqual(newstaff.username, "Jacob Lester")
        self.assertEqual(newstaff.email, "jacob55@gmail.com")
        self.assertTrue(newstaff.check_password("Jakey55"))
        self.assertEqual(newstaff.role, "staff")

    def test_staff_get_json(self):
        Teststaff = Staff(username="Jacob Lester", email="jacob55@gmail.com", password="jakey55")
        staff_json = Teststaff.get_json()
        self.assertEqual(staff_json['username'], "Jacob Lester")
        self.assertEqual(staff_json['email'], "jacob55@gmail.com")

class StudentUnitTests(unittest.TestCase):

    def test_init_student(self):
        newstudent = Student(username="Alice Smith", email="alice123@gmail.com", password="password123")
        self.assertEqual(newstudent.username, "Alice Smith")
        self.assertEqual(newstudent.email, "alice123@gmail.com")
        self.assertTrue(newstudent.check_password("password123"))
        self.assertEqual(newstudent.role, "student")
        self.assertEqual(newstudent.totalHours, 0)
        self.assertEqual(newstudent.points, 0)

    def test_student_get_json(self):
        newstudent = Student(username="Alice Smith", email="alice123@gmail.com", password="password123")
        student_json = newstudent.to_dict()
        self.assertEqual(student_json['username'], "Alice Smith")
        self.assertEqual(student_json['email'], "alice123@gmail.com")
        self.assertEqual(student_json['totalHours'], 0)
        self.assertEqual(student_json['points'], 0)

    def test_student_to_dict(self):
        newstudent = Student(username="Alice Smith", email="alice123@gmail.com", password="password123")
        newstudent.totalHours = 50
        newstudent.points = 100
        student_dict = newstudent.to_dict()
        self.assertEqual(student_dict['totalHours'], 50)
        self.assertEqual(student_dict['points'], 100)
        self.assertEqual(student_dict['studentID'], newstudent.studentID)

class RequestUnitTests(unittest.TestCase):

    def test_init_request(self):
        Testrequest = Request(student_id=12, hours=30, status='pending')
        self.assertEqual(Testrequest.student_id, 12)
        self.assertEqual(Testrequest.hours, 30)
        self.assertEqual(Testrequest.status, 'pending')
        self.assertIsInstance(Testrequest.timestamp, datetime)

    def test_request_get_json(self):
        Testrequest = Request(student_id=7, hours=15, status='approved')
        request_json = Testrequest.get_json()
        self.assertEqual(request_json['student_id'], 7)
        self.assertEqual(request_json['hours'], 15)
        self.assertEqual(request_json['status'], 'approved')
        self.assertIsNotNone(request_json['timestamp'])

    def test_request_repr(self):
        Testrequest = Request(student_id=4, hours=40, status='denied')
        rep = repr(Testrequest)
        self.assertIn("RequestID=", rep)
        self.assertIn("4", rep)
        self.assertIn("40", rep)
        self.assertIn("denied", rep)

class LoggedHoursUnitTests(unittest.TestCase):

    def test_init_loggedhours(self):
        Testlogged = LoggedHours(student_id=1, staff_id=2, hours=20, status='approved')
        self.assertEqual(Testlogged.student_id, 1)
        self.assertEqual(Testlogged.staff_id, 2)
        self.assertEqual(Testlogged.hours, 20)
        self.assertEqual(Testlogged.status, 'approved')
        self.assertIsInstance(Testlogged.timestamp, datetime)

    def test_loggedhours_get_json(self):
        Testlogged = LoggedHours(student_id=1, staff_id=2, hours=20, status='approved')
        logged_json = Testlogged.get_json()
        self.assertEqual(logged_json['student_id'], 1)
        self.assertEqual(logged_json['staff_id'], 2)
        self.assertEqual(logged_json['hours'], 20)
        self.assertEqual(logged_json['status'], 'approved')
        self.assertIsNotNone(logged_json['timestamp'])

    def test_loggedhours_repr(self):
        Testlogged = LoggedHours(student_id=1, staff_id=2, hours=20, status='approved')
        rep = repr(Testlogged)
        self.assertIn("Log ID=", rep)
        self.assertIn("1", rep)
        self.assertIn("2", rep)
        self.assertIn("20", rep)

class AccoladeUnitTests(unittest.TestCase):
    
    def test_init_accolade(self):
        Testaccolade = Accolade(accoladeID="ACC001", studentID="STU001", name="10 Hours Milestone", milestoneHours=10)
        self.assertEqual(Testaccolade.accoladeID, "ACC001")
        self.assertEqual(Testaccolade.studentID, "STU001")
        self.assertEqual(Testaccolade.name, "10 Hours Milestone")
        self.assertEqual(Testaccolade.milestoneHours, 10)
        self.assertIsInstance(Testaccolade.dateAwarded, datetime)
    
    def test_accolade_to_dict(self):
        Testaccolade = Accolade(accoladeID="ACC001", studentID="STU001", name="10 Hours Milestone", milestoneHours=10)
        accolade_dict = Testaccolade.to_dict()
        self.assertEqual(accolade_dict['accoladeID'], "ACC001")
        self.assertEqual(accolade_dict['studentID'], "STU001")
        self.assertEqual(accolade_dict['name'], "10 Hours Milestone")
        self.assertEqual(accolade_dict['milestoneHours'], 10)
        self.assertIsNotNone(accolade_dict['dateAwarded'])

class ActivityUnitTests(unittest.TestCase):
    
    def test_init_activity(self):
        Testactivity = Activity(logID="LOG001", studentID="STU001", hoursLogged=5, description="Volunteering")
        self.assertEqual(Testactivity.logID, "LOG001")
        self.assertEqual(Testactivity.studentID, "STU001")
        self.assertEqual(Testactivity.hoursLogged, 5)
        self.assertEqual(Testactivity.description, "Volunteering")
        self.assertEqual(Testactivity.status, "Pending")
        self.assertIsInstance(Testactivity.dateLogged, datetime)
    
    def test_activity_to_dict(self):
        Testactivity = Activity(logID="LOG001", studentID="STU001", hoursLogged=5, description="Volunteering")
        activity_dict = Testactivity.to_dict()
        self.assertEqual(activity_dict['logID'], "LOG001")
        self.assertEqual(activity_dict['studentID'], "STU001")
        self.assertEqual(activity_dict['hoursLogged'], 5)
        self.assertEqual(activity_dict['description'], "Volunteering")
        self.assertEqual(activity_dict['status'], "Pending")
        self.assertIsNotNone(activity_dict['dateLogged'])
    
    def test_activity_getters(self):
        Testactivity = Activity(logID="LOG001", studentID="STU001", hoursLogged=5, description="Volunteering")
        self.assertEqual(Testactivity.getHoursLogged(), 5)
        self.assertEqual(Testactivity.getDescription(), "Volunteering")


# '''
#     Integration Tests
# '''
# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

class StaffIntegrationTests(unittest.TestCase):

    def test_create_staff(self):
        staff = register_staff("marcus", "marcus@example.com", "pass123")
        assert staff.username == "marcus"
        # ensure staff persisted
        fetched = Staff.query.get(staff.staff_id)
        assert fetched is not None
        assert fetched.email == "marcus@example.com"

    def test_request_fetch(self):
        # create a student and a pending request
        student = Student.create_student("tariq", "tariq@example.com", "studpass")
        db.session.add(student)
        db.session.commit()

        req = Request(student_id=student.student_id, hours=3.5, status='pending')
        db.session.add(req)
        db.session.commit()

        requests = fetch_all_requests()
        # should include request with student name 'tariq'
        assert len(requests) >= 1
        assert any(r['student_name'] == 'tariq' and r['hours'] == 3.5 for r in requests)

    def test_hours_approval(self):
        # prepare staff, student and request
        staff = register_staff("carmichael", "carm@example.com", "staffpass")
        student = Student.create_student("niara", "niara@example.com", "studpass")
        db.session.add(student)
        db.session.commit()

        req = Request(student_id=student.student_id, hours=2.0, status='pending')
        db.session.add(req)
        db.session.commit()

        result = process_request_approval(staff.staff_id, req.id)
        
        # Validating result structure
        assert 'request' in result
        assert 'logged_hours' in result
        assert 'student_name' in result
        assert 'staff_name' in result

        # Validating request updated
        assert result['request'].status == 'approved'

        # Validating logged hours created
        logged = result['logged_hours']
        assert logged is not None
        assert logged.hours == 2.0
        assert logged.student_id == student.student_id
        assert logged.staff_id == staff.staff_id
        assert logged.status == 'approved'

    def test_hours_denial(self):
        # prepare staff, student and request
        staff = register_staff("maritza", "maritza@example.com", "staffpass")
        student = Student.create_student("jabari", "jabari@example.com", "studpass")
        db.session.add(student)
        db.session.commit()

        req = Request(student_id=student.student_id, hours=1.0, status='pending')
        db.session.add(req)
        db.session.commit()

        result = process_request_denial(staff.staff_id, req.id)
        
        # Validating response structure
        assert 'request' in result
        assert 'denial_successful' in result

        assert result['denial_successful'] is True
        assert result['request'].status == 'denied'
        assert result['student_name'] == "jabari"
        assert result['staff_name'] == "maritza"


class StudentIntegrationTests(unittest.TestCase):

    def test_create_student(self):
        student = register_student("junior", "junior@example.com", "studpass")
        assert student.username == "junior"
        fetched = Student.query.get(student.student_id)
        assert fetched is not None
        assert fetched.email == "junior@example.com"

    def test_request_hours_confirmation(self):
        student = Student.create_student("amara", "amara@example.com", "pass")
        req = create_hours_request(student.student_id, 4.0)
        assert req is not None
        assert req.hours == 4.0
        assert req.status == 'pending'

    def test_fetch_requests(self):
        student = Student.create_student("kareem", "kareem@example.com", "pass")
        # create two requests
        r1 = create_hours_request(student.student_id, 1.0)
        r2 = create_hours_request(student.student_id, 2.5)
        reqs = fetch_requests(student.student_id)
        assert len(reqs) >= 2
        hours = [r.hours for r in reqs]
        assert 1.0 in hours and 2.5 in hours

    def test_get_approved_hours_and_accolades(self):
        student = Student.create_student("nisha", "nisha@example.com", "pass")
        # Manually add logged approved hours
        lh1 = LoggedHours(student_id=student.student_id, staff_id=None, hours=6.0, status='approved')
        lh2 = LoggedHours(student_id=student.student_id, staff_id=None, hours=5.0, status='approved')
        db.session.add_all([lh1, lh2])
        db.session.commit()

        name, total = get_approved_hours(student.student_id)
        assert name == student.username
        assert total == 11.0

        accolades = fetch_accolades(student.student_id)
        # 11 hours should give at least the 10 hours accolade
        assert '10 Hours Milestone' in accolades

    def test_generate_leaderboard(self):
        # create three students with varying approved hours
        a = Student.create_student("zara", "zara@example.com", "p")
        b = Student.create_student("omar", "omar@example.com", "p")
        c = Student.create_student("leon", "leon@example.com", "p")
        db.session.add_all([
            LoggedHours(student_id=a.student_id, staff_id=None, hours=10.0, status='approved'),
            LoggedHours(student_id=b.student_id, staff_id=None, hours=5.0, status='approved'),
            LoggedHours(student_id=c.student_id, staff_id=None, hours=1.0, status='approved')
        ])
        db.session.commit()

        leaderboard = generate_leaderboard()
        # leaderboard should be ordered desc by hours for the students we created
        names = [item['name'] for item in leaderboard]
        # ensure our students are present
        assert 'zara' in names and 'omar' in names and 'leon' in names
        # assert relative ordering: zara (10) > omar (5) > leon (1)
        assert names.index('zara') < names.index('omar') < names.index('leon')

    def test_get_activity_history(self):
        student = register_student("dana", "dana@example.com", "pw")

        # Add logged hours
        lh1 = LoggedHours(student_id=student.student_id, staff_id=None, hours=4.0, status='approved')
        lh2 = LoggedHours(student_id=student.student_id, staff_id=None, hours=6.0, status='approved')
        lh3 = LoggedHours(student_id=student.student_id, staff_id=None, hours=15.0, status='approved')
        db.session.add_all([lh1, lh2, lh3])
        db.session.commit()

        history = get_activity_history(student.student_id)

        # Should return entries equal to approved logs
        assert len(history) == 3

        # Check cumulative hours and milestone triggers
        assert history[0]['cumulative_hours'] == 4.0
        assert history[0]['milestones_achieved'] == []

        assert history[1]['cumulative_hours'] == 10.0
        assert '10 Hours Milestone' in history[1]['milestones_achieved']

        assert history[2]['cumulative_hours'] == 25.0
        assert '25 Hours Milestone' in history[2]['milestones_achieved']
        
        