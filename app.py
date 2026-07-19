from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Student Table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50))
    year = db.Column(db.String(20))
    cgpa = db.Column(db.String(10))
    skills = db.Column(db.String(200))
    password = db.Column(db.String(100))


# Job Table
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    role = db.Column(db.String(100))
    package = db.Column(db.String(50))
    skills = db.Column(db.String(200))
    location = db.Column(db.String(100))


# Application Table
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student.id')
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job.id')
    )

    student = db.relationship('Student')
    job = db.relationship('Job')


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            department=request.form['department'],
            year=request.form['year'],
            cgpa=request.form['cgpa'],
            skills=request.form['skills'],
            password=request.form['password']
        )

        db.session.add(student)
        db.session.commit()

        return "Registration Successful!"

    return render_template('register.html')


# Student Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        student = Student.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if student:
            return render_template(
                'dashboard.html',
                student=student
            )

        return "Invalid Email or Password"

    return render_template('login.html')


# Admin Login
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            students = Student.query.all()

            return render_template(
                'admin.html',
                students=students
            )

        return "Invalid Admin Credentials"

    return render_template('admin_login.html')


# Admin Dashboard
@app.route('/admin')
def admin():

    students = Student.query.all()

    return render_template(
        'admin.html',
        students=students
    )


# Add Job
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():

    if request.method == 'POST':

        job = Job(
            company=request.form['company'],
            role=request.form['role'],
            package=request.form['package'],
            skills=request.form['skills'],
            location=request.form['location']
        )

        db.session.add(job)
        db.session.commit()

        return "Job Added Successfully!"

    return render_template('add_job.html')


# Student View Jobs
@app.route('/jobs')
def jobs():

    jobs = Job.query.all()

    return render_template(
        'jobs.html',
        jobs=jobs
    )


# Apply Job
@app.route('/apply/<int:job_id>')
def apply(job_id):

    application = Application(
        student_id=1,
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    return "Application Submitted Successfully!"


# Admin View Applications
@app.route('/applications')
def applications():

    applications = Application.query.all()

    return render_template(
        'applications.html',
        applications=applications
    )


# Create Database
with app.app_context():
    db.create_all()


# Run Application
if __name__ == '__main__':
    app.run(debug=True)