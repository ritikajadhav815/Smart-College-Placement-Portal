from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = "placementportal123"

# -----------------------------
# Database Configuration
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# Student Table
# -----------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50))
    year = db.Column(db.String(20))
    cgpa = db.Column(db.String(10))
    skills = db.Column(db.String(200))
    password = db.Column(db.String(100), nullable=False)


# -----------------------------
# Job Table
# -----------------------------
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    role = db.Column(db.String(100))
    package = db.Column(db.String(50))
    skills = db.Column(db.String(200))
    location = db.Column(db.String(100))


# -----------------------------
# Application Table
# -----------------------------
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

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    student = db.relationship('Student')
    job = db.relationship('Job')


# -----------------------------
# Home Page
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')


# -----------------------------
# Student Registration
# -----------------------------
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

        return redirect(url_for('login'))

    return render_template('register.html')


# -----------------------------
# Student Login
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        student = Student.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if student:

            session['student_id'] = student.id
            session['student_name'] = student.name

            return redirect(url_for('dashboard'))

        return "Invalid Email or Password"

    return render_template('login.html')


# -----------------------------
# Student Dashboard
# -----------------------------
@app.route('/dashboard')
def dashboard():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])

    applications = Application.query.filter_by(
        student_id=student.id
    ).all()

    return render_template(
        'dashboard.html',
        student=student,
        applications=applications
    )


# -----------------------------
# Student Logout
# -----------------------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('home'))


# -----------------------------
# Admin Login
# -----------------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            session['admin'] = True

            return redirect(url_for('admin'))

        return "Invalid Admin Credentials"

    return render_template('admin_login.html')
    # -----------------------------
# Admin Dashboard
# -----------------------------
@app.route('/admin')
def admin():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    students = Student.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    return render_template(
        'admin.html',
        students=students,
        total_students=len(students),
        total_jobs=len(jobs),
        total_applications=len(applications)
    )


# -----------------------------
# Add Job
# -----------------------------
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

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

        return redirect(url_for('jobs'))

    return render_template('add_job.html')


# -----------------------------
# Student View Jobs
# -----------------------------
@app.route('/jobs')
def jobs():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    jobs = Job.query.all()

    return render_template(
        'jobs.html',
        jobs=jobs
    )


# -----------------------------
# Apply for Job
# -----------------------------
@app.route('/apply/<int:job_id>')
def apply(job_id):

    if 'student_id' not in session:
        return redirect(url_for('login'))

    existing = Application.query.filter_by(
        student_id=session['student_id'],
        job_id=job_id
    ).first()

    if existing:
        return "You have already applied for this job."

    application = Application(
        student_id=session['student_id'],
        job_id=job_id,
        status="Pending"
    )

    db.session.add(application)
    db.session.commit()

    return redirect(url_for('dashboard'))


# -----------------------------
# View Applications (Admin)
# -----------------------------
@app.route('/applications')
def applications():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    applications = Application.query.all()

    return render_template(
        'applications.html',
        applications=applications
    )


# -----------------------------
# Approve Application
# -----------------------------
@app.route('/approve/<int:id>')
def approve(id):

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    application = Application.query.get_or_404(id)

    application.status = "Approved"

    db.session.commit()

    return redirect(url_for('applications'))


# -----------------------------
# Reject Application
# -----------------------------
@app.route('/reject/<int:id>')
def reject(id):

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    application = Application.query.get_or_404(id)

    application.status = "Rejected"

    db.session.commit()

    return redirect(url_for('applications'))


# -----------------------------
# Create Database
# -----------------------------
with app.app_context():
    db.create_all()


# -----------------------------
# Run Application
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)