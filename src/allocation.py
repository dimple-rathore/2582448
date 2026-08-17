import pandas as pd
from pathlib import Path


# ============================================================
# CLASSROOM ALLOCATION ENGINE
# ============================================================

# Project root = one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# ============================================================
# LOAD DATA
# ============================================================

students = pd.read_csv(DATA_DIR / "students.csv")
departments = pd.read_csv(DATA_DIR / "departments.csv")
classrooms = pd.read_csv(DATA_DIR / "classrooms.csv")
timetable = pd.read_csv(DATA_DIR / "timetable.csv")
bookings = pd.read_csv(DATA_DIR / "bookings.csv")


# ============================================================
# TIME FUNCTIONS
# ============================================================

def time_to_minutes(time_string):
    """Convert HH:MM into minutes after midnight."""

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


def times_overlap(
    requested_start,
    requested_end,
    existing_start,
    existing_end
):
    """
    Return True if two time intervals overlap.
    """

    return (
        time_to_minutes(requested_start)
        < time_to_minutes(existing_end)
        and
        time_to_minutes(existing_start)
        < time_to_minutes(requested_end)
    )


# ============================================================
# DISTANCE CATEGORY
# ============================================================

def get_distance_category(
    student_block,
    classroom_block
):
    """
    Determine categorical distance between
    student's department block and classroom block.

    Same block      -> Near
    One block away  -> Medium
    2+ blocks away  -> Far
    """

    student_number = int(
        student_block.replace("Block ", "")
    )

    classroom_number = int(
        classroom_block.replace("Block ", "")
    )

    difference = abs(
        student_number - classroom_number
    )

    if difference == 0:
        return "Near"

    elif difference == 1:
        return "Medium"

    else:
        return "Far"


# ============================================================
# DISTANCE SCORE
# ============================================================

def distance_score(distance):

    if distance == "Near":
        return 100

    elif distance == "Medium":
        return 60

    else:
        return 20


# ============================================================
# CAPACITY SCORE
# ============================================================

def capacity_score(
    classroom_capacity,
    requested_students
):
    """
    Give a higher score to classrooms that fit the
    requested number of students closely.

    A room that is too small receives 0.

    Example:
    Request = 30 students

    30 seats -> 100
    35 seats -> high score
    80 seats -> lower score
    """

    if classroom_capacity < requested_students:
        return 0

    unused_capacity = (
        classroom_capacity
        - requested_students
    )

    # Exact fit gets 100.
    # Larger unused capacity gradually lowers the score.
    score = 100 - (
        unused_capacity
        / classroom_capacity
        * 100
    )

    return round(
        max(score, 0),
        2
    )


# ============================================================
# FACILITY SCORE
# ============================================================

def facility_score(
    classroom,
    required_facilities
):
    """
    Calculate percentage of requested facilities
    available in the classroom.
    """

    if not required_facilities:
        return 100

    matched = 0

    for facility in required_facilities:

        if classroom[facility] == "Yes":
            matched += 1

    score = (
        matched
        / len(required_facilities)
        * 100
    )

    return round(score, 2)


# ============================================================
# CHECK ROOM AVAILABILITY
# ============================================================

def is_room_available(
    room_id,
    requested_date,
    requested_start,
    requested_end
):
    """
    Check both the academic timetable and existing
    student bookings.
    """

    # --------------------------------------------------------
    # Check timetable
    # --------------------------------------------------------

    room_timetable = timetable[
        (timetable["room_id"] == room_id)
        &
        (timetable["date"] == requested_date)
    ]

    for _, row in room_timetable.iterrows():

        if times_overlap(
            requested_start,
            requested_end,
            row["start_time"],
            row["end_time"]
        ):

            return False


    # --------------------------------------------------------
    # Check existing bookings
    # --------------------------------------------------------

    room_bookings = bookings[
        (bookings["room_id"] == room_id)
        &
        (bookings["date"] == requested_date)
        &
        (bookings["status"] == "Confirmed")
    ]

    for _, row in room_bookings.iterrows():

        if times_overlap(
            requested_start,
            requested_end,
            row["start_time"],
            row["end_time"]
        ):

            return False


    return True


# ============================================================
# MAIN ALLOCATION FUNCTION
# ============================================================

def recommend_classrooms(
    student_id,
    requested_date,
    requested_start,
    requested_end,
    number_of_students,
    required_facilities=None
):
    """
    Find and rank suitable classrooms.

    Parameters
    ----------
    student_id:
        Student requesting the classroom.

    requested_date:
        Date in YYYY-MM-DD format.

    requested_start:
        Start time in HH:MM format.

    requested_end:
        End time in HH:MM format.

    number_of_students:
        Number of students expected.

    required_facilities:
        List of required classroom features.

    Returns
    -------
    pandas DataFrame containing ranked classrooms.
    """

    if required_facilities is None:
        required_facilities = []


    # ========================================================
    # FIND STUDENT
    # ========================================================

    student_record = students[
        students["student_id"].astype(str)
        == str(student_id)
    ]

    if student_record.empty:

        raise ValueError(
            "Student ID not found."
        )

    student = student_record.iloc[0]


    # ========================================================
    # FIND STUDENT'S DEPARTMENT
    # ========================================================

    department_record = departments[
        departments["department_name"]
        == student["department"]
    ]

    if department_record.empty:

        raise ValueError(
            "Student department not found."
        )

    student_block = (
        department_record.iloc[0]["building"]
    )


    # ========================================================
    # FIND AVAILABLE CLASSROOMS
    # ========================================================

    recommendations = []


    for _, classroom in classrooms.iterrows():

        room_id = classroom["room_id"]


        # ----------------------------------------------------
        # 1. Availability
        # ----------------------------------------------------

        if not is_room_available(
            room_id,
            requested_date,
            requested_start,
            requested_end
        ):
            continue


        # ----------------------------------------------------
        # 2. Capacity
        # ----------------------------------------------------

        cap_score = capacity_score(
            classroom["capacity"],
            number_of_students
        )

        # Room is too small
        if cap_score == 0:
            continue


        # ----------------------------------------------------
        # 3. Distance
        # ----------------------------------------------------

        distance = get_distance_category(
            student_block,
            classroom["building"]
        )

        dist_score = distance_score(
            distance
        )


        # ----------------------------------------------------
        # 4. Facilities
        # ----------------------------------------------------

        fac_score = facility_score(
            classroom,
            required_facilities
        )


        # ----------------------------------------------------
        # 5. Overall weighted score
        # ----------------------------------------------------

        overall_score = (
            0.40 * dist_score
            +
            0.30 * cap_score
            +
            0.30 * fac_score
        )


        recommendations.append({

            "room_id":
                room_id,

            "building":
                classroom["building"],

            "floor":
                classroom["floor"],

            "capacity":
                classroom["capacity"],

            "distance":
                distance,

            "distance_score":
                dist_score,

            "capacity_score":
                cap_score,

            "facility_score":
                fac_score,

            "overall_score":
                round(
                    overall_score,
                    2
                ),

            "projector":
                classroom["projector"],

            "smart_board":
                classroom["smart_board"],

            "computers":
                classroom["computers"],

            "wifi":
                classroom["wifi"],

            "air_conditioning":
                classroom["air_conditioning"]
        })


    # ========================================================
    # CONVERT TO DATAFRAME
    # ========================================================

    result = pd.DataFrame(
        recommendations
    )


       # ========================================================
    # SORT BY OVERALL SCORE
    # ========================================================

    if not result.empty:
        result = result.sort_values(
            by=[
                "overall_score",
                "capacity_score",
                "floor",
                "room_id"
            ],
            ascending=[
                False,
                False,
                True,
                True
            ]
        ).reset_index(drop=True)

        result.insert(
            0,
            "rank",
            range(1, len(result) + 1)
        )

    return result


# ============================================================
# TEST THE ALLOCATION ENGINE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("CLASSROOM ALLOCATION TEST")
    print("=" * 70)


    # --------------------------------------------------------
    # Example request
    #
    # Student 1000002 = Aarav Bhat
    # Department = Data Science
    # Data Science = Block 1
    # --------------------------------------------------------

    recommendations = recommend_classrooms(

        student_id="1000002",

        requested_date="2026-08-22",

        requested_start="14:00",

        requested_end="16:00",

        number_of_students=35,

        required_facilities=[
            "projector",
            "smart_board"
        ]
    )


    print()
    print("REQUEST")
    print("-" * 70)

    print("Student ID:       1000002")
    print("Department:       Data Science")
    print("Date:             2026-08-22")
    print("Time:             14:00 - 16:00")
    print("Students:         35")
    print("Required:         Projector, Smart Board")


    print()
    print("RECOMMENDED CLASSROOMS")
    print("-" * 70)


    if recommendations.empty:

        print(
            "No suitable classrooms found."
        )

    else:

        columns_to_display = [
            "rank",
            "room_id",
            "building",
            "floor",
            "capacity",
            "distance",
            "capacity_score",
            "facility_score",
            "overall_score"
        ]

        print(
            recommendations[
                columns_to_display
            ].head(10).to_string(
                index=False
            )
        )

    print()
    print("=" * 70)
    print("ALLOCATION TEST COMPLETE")
    print("=" * 70)