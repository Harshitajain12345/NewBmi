from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func  # Importing for aggregate functions

app = Flask(__name__)

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/bmi_calculator'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    age = db.Column(db.Integer, nullable=False)     # Age field
    height = db.Column(db.Float, nullable=False)    # Height field in cm
    weight = db.Column(db.Float, nullable=False)     # Weight field in kg
    bmi = db.Column(db.Float, nullable=False)        # BMI value
    category = db.Column(db.String(50), nullable=False)  # Health condition

    def __repr__(self):
        return f'<User {self.id}: BMI={self.bmi}, Category={self.category}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Retrieve data from the form
    age = int(request.form['age'])
    height = float(request.form['height']) / 100  # convert cm to meters
    weight = float(request.form['weight'])

    print(f"Age: {age}, Height: {height * 100}, Weight: {weight}")  # Debugging line

    # Calculate BMI
    bmi = weight / (height ** 2)

    # Determine category based on BMI
    if bmi < 18.5:
        category = "Underweight"
        message = "You are underweight. Click the button for a personalized diet and exercise plan."
        chart_button = True
    elif 18.5 <= bmi < 24.9:
        category = "Normal"
        message = "You have a normal BMI. Continue to maintain your current diet and lifestyle."
        chart_button = False
    elif 25 <= bmi < 29.9:
        category = "Overweight"
        message = "You are overweight. Click the button for a personalized diet and exercise plan."
        chart_button = True
    else:
        category = "Obese"
        message = "You are obese. Click the button for a personalized diet and exercise plan."
        chart_button = True

    # Create a new User instance and add to database
    new_user = User(age=age, height=height * 100, weight=weight, bmi=bmi, category=category)  # Store height in cm
    db.session.add(new_user)
    
    # Debugging: Print the data being saved
    print(f'Saving data: Age={age}, Height={height * 100}, Weight={weight}, BMI={bmi}, Category={category}')

    try:
        db.session.commit()  # Commit the changes
        print("Data committed successfully!")  # Success message
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error occurred: {e}")  # Print any errors that occur

    return render_template('index.html', bmi=bmi, category=category, message=message, chart_button=chart_button)

@app.route('/users')
def users():
    # Fetch all users from the database
    users = User.query.all()  # This retrieves all user records
    print(users)  # Print the fetched users to the console
    return render_template('users.html', users=users)  # Pass the users to the template

@app.route('/statistics')
def statistics():
    total_users = User.query.count()  # Get total number of users
    average_bmi = db.session.query(func.avg(User.bmi)).scalar()  # Calculate average BMI

    # Count users in each category
    underweight_count = User.query.filter_by(category='Underweight').count()
    normal_count = User.query.filter_by(category='Normal').count()
    overweight_count = User.query.filter_by(category='Overweight').count()
    obese_count = User.query.filter_by(category='Obese').count()

    return render_template('statistics.html', total_users=total_users, average_bmi=average_bmi,
                           underweight_count=underweight_count, normal_count=normal_count,
                           overweight_count=overweight_count, obese_count=obese_count)

@app.route('/PowerFit_plus')
def PowerFit_plus():
    return render_template('PowerFit_plus.html')

@app.route('/personalized-chart/<category>')
def personalized_chart(category):
    # Define diet and exercise charts based on category
    charts = {
        "Underweight": {
            "diet": [
                "Increase calorie intake with nutrient-dense foods.",
                "Include more proteins like eggs, chicken, fish, and legumes.",
                "Consume healthy fats like avocado, nuts, seeds, and olive oil."
            ],
            "exercise": [
                "Vrikshasana (Tree Pose): Helps improve balance and stability.",
                "Bhujangasana (Cobra Pose): Strengthens the spine and reduces stress."
            ]
        },
        "Overweight": {
            "diet": [
                "Focus on portion control and avoid overeating.",
                "Include more fiber-rich foods like vegetables, fruits, and whole grains."
            ],
            "exercise": [
                "Trikonasana (Triangle Pose): Reduces fat and strengthens muscles.",
                "Surya Namaskar (Sun Salutation): Enhances metabolism and burns calories."
            ]
        },
        "Obese": {
            "diet": [
                "Focus on a balanced, low-calorie diet with lean proteins and vegetables.",
                "Limit processed foods, sugary drinks, and fried foods."
            ],
            "exercise": [
                "Virabhadrasana (Warrior Pose): Increases stamina and promotes weight loss.",
                "Pranayama (Breathing exercises): Reduces stress and helps with weight management."
            ]
        }
    }

    # Get the specific chart based on the category
    chart = charts.get(category, None)

    # Render the template and pass the chart and category data
    return render_template('personalized_chart.html', chart=chart, category=category)

if __name__ == '__main__':
    with app.app_context():  # Create application context
        db.create_all()  # Create database tables
    app.run(debug=True)  # Run the Flask app
