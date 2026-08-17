import csv
import random
from datetime import date, timedelta
from pathlib import Path

# ============================================================
# CLASSROOM ALLOCATION PROJECT
# Synthetic Dataset Generator
# ============================================================

# Reproducible data
random.seed(42)

# Project root = one level above the src folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Create data folder if it does not exist
DATA_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. BUILDINGS
# ============================================================

buildings = [
    {"building": "Block 1", "location_order": 1},
    {"building": "Block 2", "location_order": 2},
    {"building": "Block 3", "location_order": 3},
    {"building": "Block 4", "location_order": 4},
    {"building": "Block 5", "location_order": 5},
]


# ============================================================
# 2. DEPARTMENTS
# Two departments in each block
# ============================================================

departments = [
    {"department_id": "D01", "department_name": "Computer Science", "building": "Block 1"},
    {"department_id": "D02", "department_name": "Data Science", "building": "Block 1"},

    {"department_id": "D03", "department_name": "Mathematics", "building": "Block 2"},
    {"department_id": "D04", "department_name": "Physics", "building": "Block 2"},

    {"department_id": "D05", "department_name": "Commerce", "building": "Block 3"},
    {"department_id": "D06", "department_name": "Economics", "building": "Block 3"},

    {"department_id": "D07", "department_name": "English", "building": "Block 4"},
    {"department_id": "D08", "department_name": "Psychology", "building": "Block 4"},

    {"department_id": "D09", "department_name": "Biotechnology", "building": "Block 5"},
    {"department_id": "D10", "department_name": "Statistics", "building": "Block 5"},
]


# ============================================================
# 3. STUDENTS
# 200 students
# Unique 7-digit IDs
# Names alphabetically sorted
# Password = name
# ============================================================

first_names = [
    "Aarav", "Aditi", "Akash", "Alisha", "Aman",
    "Ananya", "Arjun", "Aryan", "Bhavya", "Bharat",
    "Charan", "Diya", "Esha", "Farhan", "Gauri",
    "Harish", "Ishita", "Jatin", "Karan", "Kavya",
    "Kiran", "Lakshmi", "Manish", "Meera", "Naina",
    "Nikhil", "Pallavi", "Pranav", "Priya", "Rahul",
    "Riya", "Rohan", "Sakshi", "Sameer", "Shreya",
    "Sneha", "Tanvi", "Varun", "Vikas", "Zoya"
]

last_names = [
    "Bansal", "Bhat", "Chandra", "Das", "Desai",
    "Gupta", "Iyer", "Joshi", "Kapoor", "Khan",
    "Mehta", "Menon", "Mishra", "Nair", "Patel",
    "Rao", "Reddy", "Shah", "Sharma", "Singh",
    "Sinha", "Thomas", "Verma", "Yadav"
]

# Generate combinations and sort alphabetically
all_names = sorted(
    f"{first} {last}"
    for first in first_names
    for last in last_names
)

# Take first 200
student_names = all_names[:200]

department_names = [
    department["department_name"]
    for department in departments
]

students = []

for number, name in enumerate(student_names, start=1):

    # 1000001, 1000002, ...
    student_id = str(1000000 + number)

    department = department_names[(number - 1) % 10]

    students.append({
        "student_id": student_id,
        "name": name,
        "department": department,
        "password": name
    })


# ============================================================
# 4. CLASSROOMS
# 60 classrooms per block
# Total = 300 classrooms
# ============================================================

classrooms = []

capacities = [
    20, 25, 30, 35, 40,
    45, 50, 60, 70, 80
]

for block_number in range(1, 6):

    for room_number in range(1, 61):

        room_id = f"R{block_number}{room_number:02d}"

        # 15 rooms per floor
        floor = ((room_number - 1) // 15) + 1

        capacity = random.choice(capacities)

        projector = "Yes" if random.random() < 0.82 else "No"

        smart_board = "Yes" if random.random() < 0.65 else "No"

        computers = "Yes" if random.random() < 0.28 else "No"

        wifi = "Yes" if random.random() < 0.95 else "No"

        air_conditioning = (
            "Yes" if random.random() < 0.55 else "No"
        )

        classrooms.append({
            "room_id": room_id,
            "building": f"Block {block_number}",
            "floor": floor,
            "capacity": capacity,
            "projector": projector,
            "smart_board": smart_board,
            "computers": computers,
            "wifi": wifi,
            "air_conditioning": air_conditioning
        })


# ============================================================
# 5. TIMETABLE
#
# Academic period:
# 17-Aug-2026 to 26-Aug-2026
#
# Most rooms receive multiple schedules.
# First 30 rooms receive only ONE schedule.
# No overlapping schedules are created for the same room.
# ============================================================

start_date = date(2026, 8, 17)

number_of_days = 10

time_slots = [
    ("08:00", "10:00"),
    ("10:00", "12:00"),
    ("12:00", "13:00"),
    ("13:00", "15:00"),
    ("15:00", "17:00"),
    ("17:00", "19:00")
]

activities = [
    "Lecture",
    "Tutorial",
    "Lab",
    "Seminar",
    "Workshop"
]

timetable = []

schedule_number = 1

for room_index, room in enumerate(classrooms):

    # First 30 rooms have only one schedule
    if room_index < 30:
        number_of_schedules = 1

    else:
        number_of_schedules = random.randint(3, 7)

    possible_slots = []

    for day_number in range(number_of_days):

        current_date = start_date + timedelta(days=day_number)

        for slot_number, slot in enumerate(time_slots):

            possible_slots.append({
                "date": current_date,
                "start_time": slot[0],
                "end_time": slot[1],
                "slot_number": slot_number
            })

    # Randomly select schedules
    selected_slots = random.sample(
        possible_slots,
        number_of_schedules
    )

    # Sort selected schedules chronologically
    selected_slots.sort(
        key=lambda x: (
            x["date"],
            x["slot_number"]
        )
    )

    for slot in selected_slots:

        timetable.append({
            "schedule_id": f"T{schedule_number:04d}",
            "room_id": room["room_id"],
            "date": slot["date"].isoformat(),
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "activity": random.choice(activities)
        })

        schedule_number += 1


# ============================================================
# TIME HELPER FUNCTIONS
# ============================================================

def time_to_minutes(time_string):

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


def times_overlap(
    start1,
    end1,
    start2,
    end2
):

    return (
        time_to_minutes(start1)
        < time_to_minutes(end2)
        and
        time_to_minutes(start2)
        < time_to_minutes(end1)
    )


# ============================================================
# 6. BOOKINGS
#
# Generate 120 valid bookings.
#
# A booking cannot:
# - overlap a timetable entry
# - overlap another booking in the same room
# - conflict with another booking made by the same student
# ============================================================

bookings = []

booking_number = 1

booking_activities = [
    "Project Work",
    "Group Discussion",
    "Club Meeting",
    "Guest Lecture",
    "Makeup Class"
]

booking_time_slots = [
    ("08:00", "09:00"),
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("16:00", "17:00"),
    ("17:00", "18:00")
]

booking_dates = [
    (
        start_date
        + timedelta(days=day)
    ).isoformat()
    for day in range(number_of_days)
]


# Store occupied periods
# Key = room + date
occupied_periods = {}

for entry in timetable:

    key = (
        entry["room_id"],
        entry["date"]
    )

    if key not in occupied_periods:
        occupied_periods[key] = []

    occupied_periods[key].append(
        (
            entry["start_time"],
            entry["end_time"]
        )
    )


attempts = 0

while len(bookings) < 120 and attempts < 10000:

    attempts += 1

    room = random.choice(classrooms)

    booking_date = random.choice(
        booking_dates
    )

    start_time, end_time = random.choice(
        booking_time_slots
    )

    key = (
        room["room_id"],
        booking_date
    )

    existing_periods = occupied_periods.get(
        key,
        []
    )

    # Check room availability
    room_conflict = False

    for existing_start, existing_end in existing_periods:

        if times_overlap(
            start_time,
            end_time,
            existing_start,
            existing_end
        ):

            room_conflict = True
            break

    if room_conflict:
        continue

    student = random.choice(students)

    # Check whether student already has a conflicting booking
    student_conflict = False

    for existing_booking in bookings:

        if (
            existing_booking["student_id"]
            == student["student_id"]
            and
            existing_booking["date"]
            == booking_date
        ):

            if times_overlap(
                start_time,
                end_time,
                existing_booking["start_time"],
                existing_booking["end_time"]
            ):

                student_conflict = True
                break

    if student_conflict:
        continue

    # Create booking
    booking = {
        "booking_id": f"B{booking_number:04d}",
        "student_id": student["student_id"],
        "room_id": room["room_id"],
        "date": booking_date,
        "start_time": start_time,
        "end_time": end_time,
        "activity": random.choice(
            booking_activities
        ),
        "status": "Confirmed"
    }

    bookings.append(booking)

    occupied_periods.setdefault(
        key,
        []
    ).append(
        (
            start_time,
            end_time
        )
    )

    booking_number += 1


# ============================================================
# CSV WRITING FUNCTION
# ============================================================

def write_csv(
    filename,
    rows,
    fieldnames
):

    file_path = DATA_DIR / filename

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)


# ============================================================
# WRITE ALL SIX DATASETS
# ============================================================

write_csv(
    "buildings.csv",
    buildings,
    [
        "building",
        "location_order"
    ]
)

write_csv(
    "departments.csv",
    departments,
    [
        "department_id",
        "department_name",
        "building"
    ]
)

write_csv(
    "students.csv",
    students,
    [
        "student_id",
        "name",
        "department",
        "password"
    ]
)

write_csv(
    "classrooms.csv",
    classrooms,
    [
        "room_id",
        "building",
        "floor",
        "capacity",
        "projector",
        "smart_board",
        "computers",
        "wifi",
        "air_conditioning"
    ]
)

write_csv(
    "timetable.csv",
    timetable,
    [
        "schedule_id",
        "room_id",
        "date",
        "start_time",
        "end_time",
        "activity"
    ]
)

write_csv(
    "bookings.csv",
    bookings,
    [
        "booking_id",
        "student_id",
        "room_id",
        "date",
        "start_time",
        "end_time",
        "activity",
        "status"
    ]
)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 60)
print("CLASSROOM ALLOCATION DATA GENERATION COMPLETE")
print("=" * 60)

print()
print(f"Students:      {len(students)}")
print(f"Departments:   {len(departments)}")
print(f"Buildings:     {len(buildings)}")
print(f"Classrooms:    {len(classrooms)}")
print(f"Timetable:     {len(timetable)}")
print(f"Bookings:      {len(bookings)}")

print()
print(f"Data saved to:")
print(DATA_DIR)

print()
print("Files created:")
print("  students.csv")
print("  departments.csv")
print("  buildings.csv")
print("  classrooms.csv")
print("  timetable.csv")
print("  bookings.csv")

print()
print("Dataset generation finished successfully.")