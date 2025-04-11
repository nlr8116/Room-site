from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
app = Flask(__name__, template_folder = "templetes")

CORS(app)



# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the table structure
class RoomData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(100), nullable=False)
    available = db.Column(db.String(100), nullable=False)

# Create the database table
with app.app_context():
    db.create_all()

# Route to handle form submission
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        room_number = request.form["roomNumber"]
        available = request.form["available"]

        # Create a new record
        new_data = RoomData(room_number=room_number, available=available)
        db.session.add(new_data)
        db.session.commit()

        return "Data added to database!"

    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_data():
    room_number = request.form.get("roomNumber")
    available = request.form.get("available")

    if room_number and available:
        try:
            new_entry = RoomData(room_number=room_number, available=available)
            db.session.add(new_entry)
            db.session.commit()
            return render_template("submit.html", success=True)
        except Exception as e:
            print(f"Error: {e}")
            return render_template("submit.html", success=False)
    else:
        return render_template("submit.html", success=False)


# Route to display submitted data
@app.route("/view-data")
def view_data():
    # Fetch all data from the RoomData table
    all_data = RoomData.query.all()
    return render_template("view_data.html", data=all_data)

@app.route("/clear-data")
def clear_data():
    try:
        # Delete all records in the RoomData table
        num_deleted = RoomData.query.delete()
        db.session.commit()
        return render_template("clear_data.html", success=True, num_deleted=num_deleted)
    except Exception as e:
        return render_template("clear_data.html", success=False, error=str(e))
if __name__ == '__main__':
    app.run(debug=True, host = "0.0.0.0", port = "8000")