from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from detectionTest import count_faces
import cv2
from time import sleep
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
#Route to handle sumisiion of room data
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

@app.route("/wyly-room")
def wyly_room():
    # Filter records where room_number starts with 'WYTR'
    filtered_data = RoomData.query.filter(RoomData.room_number.like("WYTR%")).all()
    return render_template("wyly_room.html", data=filtered_data)

# Route to display submitted data
@app.route("/view-data")
def view_data():
    # Filter records where room_number starts with 'IESB'
    filtered_data = RoomData.query.filter(RoomData.room_number.like("IESB%")).all()
    return render_template("view_data.html", data=filtered_data)
#route to clear data if large amount of rooms have changed
@app.route("/clear-data")
def clear_data():
    try:
        # Delete all records in the RoomData table
        num_deleted = RoomData.query.delete()
        db.session.commit()
        return render_template("clear_data.html", success=True, num_deleted=num_deleted)
    except Exception as e:
        return render_template("clear_data.html", success=False, error=str(e))

#route to handle if room becomes avalible or not
@app.route("/update-room/<room_number>", methods=["GET", "POST"])
def update_room(room_number=None):
    room = RoomData.query.filter_by(room_number=room_number).first()

    if not room:
        return render_template(
            "update_status.html",
            success=False,
            error_message=f"No room found with room number {room_number}."
        )

    while True:
        # Capture a frame from the webcam
        video_capture = cv2.VideoCapture(0)
        ret, frame = video_capture.read()
        video_capture.release()

        # Detect faces and update room availability
        face_count = count_faces(frame)
        is_available = True if face_count > 0 else False

        # Update the database
        room.available = str(is_available)  # Store as string to match DB
        db.session.commit()
        
        # Print status for debugging purposes
        print(f"Room {room_number} updated. Availability: {is_available}")

        # Optionally add a delay between checks
        sleep(5)  # Pause for 5 seconds before the next iteration


@app.route("/sudo")
def sudo():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=False, host = "0.0.0.0", port = "8000")