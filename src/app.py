import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, time
from llm import generate_explanation

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

students = pd.read_csv(DATA_DIR / "students.csv")
departments = pd.read_csv(DATA_DIR / "departments.csv")
classrooms = pd.read_csv(DATA_DIR / "classrooms.csv")
timetable = pd.read_csv(DATA_DIR / "timetable.csv")

bookings_file = DATA_DIR / "bookings.csv"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="University Classroom Allocation",
    page_icon="🏫",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "student" not in st.session_state:
    st.session_state.student = None

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "booking_details" not in st.session_state:
    st.session_state.booking_details = None


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title("🏫 University Classroom Allocation System")

    st.subheader("Student Login")

    student_id = st.text_input(
        "Student ID",
        placeholder="Enter your 7-digit Student ID"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_button = st.button(
        "Login",
        type="primary"
    )

    if login_button:

        student_record = students[
            (students["student_id"].astype(str) == student_id)
            &
            (students["password"] == password)
        ]

        if student_record.empty:

            st.error("Invalid Student ID or Password.")

        else:

            st.session_state.logged_in = True
            st.session_state.student = student_record.iloc[0]

            st.rerun()


# ============================================================
# MAIN APPLICATION
# ============================================================

else:

    student = st.session_state.student

    student_department = student["department"]

    department_record = departments[
        departments["department_name"] == student_department
    ].iloc[0]

    student_block = department_record["building"]


    # ========================================================
    # HEADER
    # ========================================================

    st.title("🏫 University Classroom Allocation System")

    st.caption(
        "Smart classroom recommendation and booking portal"
    )

    col1, col2 = st.columns([4, 1])

    with col1:

        st.subheader(
            f"Welcome, {student['name']} 👋"
        )

        st.write(
            f"**Student ID:** {student['student_id']}"
        )

        st.write(
            f"**Department:** {student_department}  |  "
            f"**Department Location:** {student_block}"
        )

    with col2:

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.student = None
            st.session_state.recommendations = None
            st.session_state.booking_details = None

            st.rerun()


    st.divider()

    # ========================================================
    # MY BOOKINGS
    # ========================================================

    st.subheader("📋 My Bookings")

    current_bookings = pd.read_csv(bookings_file)

    my_bookings = current_bookings[
        current_bookings["student_id"].astype(str)
        == str(student["student_id"])
    ].copy()

    if my_bookings.empty:

        st.info(
            "You do not have any bookings yet."
        )

    else:

        my_bookings = my_bookings.sort_values(
            by=["date", "start_time"],
            ascending=[False, False]
        )

        for _, booking in my_bookings.iterrows():

            room_info = classrooms[
                classrooms["room_id"]
                == booking["room_id"]
            ]

            if not room_info.empty:
                building = room_info.iloc[0]["building"]
                floor = room_info.iloc[0]["floor"]
            else:
                building = "Unknown"
                floor = "Unknown"

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.markdown(
                        f"### 🎫 {booking['booking_id']}"
                    )

                    st.write(
                        f"🏫 **Classroom:** "
                        f"{booking['room_id']}"
                    )

                    st.write(
                        f"📍 **Location:** "
                        f"{building}, Floor {floor}"
                    )

                    st.write(
                        f"📅 **Date:** "
                        f"{booking['date']}"
                    )

                    st.write(
                        f"🕐 **Time:** "
                        f"{booking['start_time']} – "
                        f"{booking['end_time']}"
                    )

                    st.write(
                        f"📌 **Activity:** "
                        f"{booking['activity']}"
                    )

                with col2:

                    if booking["status"] == "Confirmed":

                        st.success(
                            "✓ Confirmed"
                        )

                    else:

                        st.warning(
                            booking["status"]
                        )

    st.divider()


    # ========================================================
    # BOOKING FORM
    # ========================================================

    st.subheader("📅 Book a Classroom")

    col1, col2 = st.columns(2)

    with col1:

        booking_date = st.date_input(
            "Date",
            value=date.today()
        )

        start_time = st.time_input(
            "Start Time",
            value=time(9, 0)
        )

    with col2:

        end_time = st.time_input(
            "End Time",
            value=time(11, 0)
        )

        student_count = st.number_input(
            "Number of Students",
            min_value=1,
            max_value=100,
            value=30,
            step=1
        )


    activity = st.selectbox(
        "Activity",
        [
            "Project Work",
            "Group Discussion",
            "Makeup Class",
            "Club Meeting",
            "Guest Lecture",
            "Other"
        ]
    )


    st.write("**Required Facilities**")

    col1, col2, col3 = st.columns(3)

    with col1:

        projector = st.checkbox("Projector")
        smart_board = st.checkbox("Smart Board")

    with col2:

        computers = st.checkbox("Computers")
        wifi = st.checkbox("Wi-Fi")

    with col3:

        air_conditioning = st.checkbox(
            "Air Conditioning"
        )


    find_button = st.button(
        "🔍 Find Available Classrooms",
        type="primary"
    )


    # ========================================================
    # FIND CLASSROOMS
    # ========================================================

    if find_button:

        # ----------------------------------------------------
        # VALIDATE TIME
        # ----------------------------------------------------

        if end_time <= start_time:

            st.error(
                "End time must be later than start time."
            )

            st.session_state.recommendations = None

        else:

            requested_date = str(booking_date)
            requested_start = start_time.strftime("%H:%M")
            requested_end = end_time.strftime("%H:%M")


            # ------------------------------------------------
            # FIND OCCUPIED ROOMS FROM TIMETABLE
            # ------------------------------------------------

            day_schedule = timetable[
                timetable["date"].astype(str) == requested_date
            ]

            occupied_rooms = set()

            for _, schedule in day_schedule.iterrows():

                existing_start = schedule["start_time"]
                existing_end = schedule["end_time"]

                if (
                    requested_start < existing_end
                    and requested_end > existing_start
                ):

                    occupied_rooms.add(
                        schedule["room_id"]
                    )


            # ------------------------------------------------
            # ALSO CHECK EXISTING BOOKINGS
            # ------------------------------------------------

            current_bookings = pd.read_csv(
                bookings_file
            )

            day_bookings = current_bookings[
                (
                    current_bookings["date"].astype(str)
                    == requested_date
                )
                &
                (
                    current_bookings["status"]
                    == "Confirmed"
                )
            ]

            for _, booking in day_bookings.iterrows():

                existing_start = booking["start_time"]
                existing_end = booking["end_time"]

                if (
                    requested_start < existing_end
                    and requested_end > existing_start
                ):

                    occupied_rooms.add(
                        booking["room_id"]
                    )


            # ------------------------------------------------
            # AVAILABLE ROOMS
            # ------------------------------------------------

            available_rooms = classrooms[
                ~classrooms["room_id"].isin(occupied_rooms)
            ].copy()


            # ------------------------------------------------
            # CAPACITY FILTER
            # ------------------------------------------------

            available_rooms = available_rooms[
                available_rooms["capacity"] >= student_count
            ].copy()


            # ------------------------------------------------
            # FACILITY FILTER
            # ------------------------------------------------

            required_facilities = []

            if projector:
                required_facilities.append("projector")

            if smart_board:
                required_facilities.append("smart_board")

            if computers:
                required_facilities.append("computers")

            if wifi:
                required_facilities.append("wifi")

            if air_conditioning:
                required_facilities.append(
                    "air_conditioning"
                )


            for facility in required_facilities:

                available_rooms = available_rooms[
                    available_rooms[facility].str.lower()
                    == "yes"
                ]


            # ------------------------------------------------
            # DISTANCE
            # ------------------------------------------------

            block_number = int(
                student_block.replace("Block ", "")
            )


            def calculate_distance(room_block):

                room_number = int(
                    room_block.replace("Block ", "")
                )

                difference = abs(
                    block_number - room_number
                )

                if difference == 0:
                    return "Near"

                elif difference == 1:
                    return "Medium"

                else:
                    return "Far"


            available_rooms["distance"] = (
                available_rooms["building"]
                .apply(calculate_distance)
            )


            # ------------------------------------------------
            # CAPACITY SCORE
            # ------------------------------------------------

            available_rooms["capacity_score"] = (
                student_count
                / available_rooms["capacity"]
                * 100
            )

            available_rooms["capacity_score"] = (
                available_rooms["capacity_score"]
                .clip(upper=100)
            )


            # ------------------------------------------------
            # FACILITY SCORE
            # ------------------------------------------------

            available_rooms["facility_score"] = 100.0


            # ------------------------------------------------
            # DISTANCE SCORE
            # ------------------------------------------------

            distance_scores = {
                "Near": 100,
                "Medium": 70,
                "Far": 40
            }

            available_rooms["distance_score"] = (
                available_rooms["distance"]
                .map(distance_scores)
            )


            # ------------------------------------------------
            # OVERALL SCORE
            # ------------------------------------------------

            available_rooms["overall_score"] = (

                available_rooms["capacity_score"] * 0.50

                + available_rooms["facility_score"] * 0.30

                + available_rooms["distance_score"] * 0.20
            )


            # ------------------------------------------------
            # SORT
            # ------------------------------------------------

            available_rooms = available_rooms.sort_values(
                by=[
                    "overall_score",
                    "capacity_score",
                    "distance_score",
                    "floor",
                    "room_id"
                ],
                ascending=[
                    False,
                    False,
                    False,
                    True,
                    True
                ]
            ).reset_index(drop=True)


            # ------------------------------------------------
            # STORE TOP 5
            # ------------------------------------------------

            if available_rooms.empty:

                st.session_state.recommendations = None

                st.warning(
                    "No classrooms are available for "
                    "the selected requirements."
                )

            else:

                st.session_state.recommendations = (
                    available_rooms.head(5).copy()
                )


    # ========================================================
    # DISPLAY RECOMMENDATIONS
    # ========================================================

    if st.session_state.recommendations is not None:

        results = (
            st.session_state.recommendations.copy()
        )

        results.insert(
            0,
            "Rank",
            range(1, len(results) + 1)
        )

        results["overall_score"] = (
            results["overall_score"].round(2)
        )

        results["capacity_score"] = (
            results["capacity_score"].round(2)
        )


        st.divider()
        st.subheader(
            "🏆 Top Classroom Recommendations"
        )

        st.write(
            "These classrooms are ranked according to "
            "capacity suitability, required facilities, "
            "and distance from your department."
        )


        # ----------------------------------------------------
        # RECOMMENDATION CARDS
        # ----------------------------------------------------

        for _, room in results.iterrows():

            rank = int(room["Rank"])

            if rank == 1:
                rank_label = "🥇"
            elif rank == 2:
                rank_label = "🥈"
            elif rank == 3:
                rank_label = "🥉"
            else:
                rank_label = f"#{rank}"


            with st.container(border=True):

                col1, col2 = st.columns(
                    [3, 1]
                )


                with col1:

                    st.markdown(
                        f"### {rank_label} "
                        f"{room['room_id']}"
                    )

                    st.write(
                        f"🏫 **Location:** "
                        f"{room['building']} • "
                        f"Floor {room['floor']}"
                    )

                    st.write(
                        f"👥 **Capacity:** "
                        f"{room['capacity']} students"
                    )

                    st.write(
                        f"📍 **Distance:** "
                        f"{room['distance']}"
                    )


                with col2:

                    st.metric(
                        "Match Score",
                        f"{room['overall_score']:.2f}"
                    )


                st.write(
                    f"📊 **Capacity Score:** "
                    f"{room['capacity_score']:.2f}"
                )

                facility_text = []

                if str(
                    room["projector"]
                ).lower() == "yes":

                    facility_text.append(
                        "Projector ✓"
                    )

                if str(
                    room["smart_board"]
                ).lower() == "yes":

                    facility_text.append(
                        "Smart Board ✓"
                    )

                if str(
                    room["computers"]
                ).lower() == "yes":

                    facility_text.append(
                        "Computers ✓"
                    )

                if str(
                    room["wifi"]
                ).lower() == "yes":

                    facility_text.append(
                        "Wi-Fi ✓"
                    )

                if str(
                    room["air_conditioning"]
                ).lower() == "yes":

                    facility_text.append(
                        "Air Conditioning ✓"
                    )

                st.write(
                    " | ".join(facility_text)
                )


        # ----------------------------------------------------
        # ROOM SELECTION
        # ----------------------------------------------------

        room_options = results[
            "room_id"
        ].tolist()

        selected_room = st.selectbox(
            "Select a Classroom",
            room_options
        )


        selected_room_data = results[
            results["room_id"] == selected_room
        ].iloc[0]


        st.info(
            f"Selected: {selected_room} | "
            f"{selected_room_data['building']} | "
            f"Floor {selected_room_data['floor']} | "
            f"Capacity {selected_room_data['capacity']} | "
            f"Distance: {selected_room_data['distance']} | "
            f"Score: {selected_room_data['overall_score']:.2f}"
        )


        # ------------------------------------------------
        # GENAI EXPLANATION
        # ------------------------------------------------

        with st.expander(
            "🤖 AI Explanation for This Classroom",
            expanded=True
        ):

            explanation = generate_explanation(
                room_id=selected_room,
                building=selected_room_data["building"],
                floor=selected_room_data["floor"],
                capacity=selected_room_data["capacity"],
                distance=selected_room_data["distance"],
                capacity_score=selected_room_data["capacity_score"],
                facility_score=selected_room_data["facility_score"],
                required_facilities=required_facilities
            )

            st.write(explanation)


        confirm_button = st.button(
            "Γ£à Confirm Classroom",
   	   type="primary"
        )


        # ====================================================
        # CONFIRM BOOKING
        # ====================================================

        if confirm_button:

            requested_date = str(booking_date)

            requested_start = (
                start_time.strftime("%H:%M")
            )

            requested_end = (
                end_time.strftime("%H:%M")
            )


            # ------------------------------------------------
            # RELOAD BOOKINGS
            # ------------------------------------------------

            current_bookings = pd.read_csv(
                bookings_file
            )


            # ------------------------------------------------
            # CHECK BOOKING CONFLICT
            # ------------------------------------------------

            conflict = current_bookings[
                (
                    current_bookings["room_id"]
                    == selected_room
                )
                &
                (
                    current_bookings["date"].astype(str)
                    == requested_date
                )
                &
                (
                    current_bookings["status"]
                    == "Confirmed"
                )
                &
                (
                    current_bookings["start_time"]
                    < requested_end
                )
                &
                (
                    current_bookings["end_time"]
                    > requested_start
                )
            ]


            # ------------------------------------------------
            # CHECK TIMETABLE CONFLICT
            # ------------------------------------------------

            timetable_conflict = timetable[
                (
                    timetable["room_id"]
                    == selected_room
                )
                &
                (
                    timetable["date"].astype(str)
                    == requested_date
                )
                &
                (
                    timetable["start_time"]
                    < requested_end
                )
                &
                (
                    timetable["end_time"]
                    > requested_start
                )
            ]


            # ------------------------------------------------
            # CONFLICT FOUND
            # ------------------------------------------------

            if (
                not conflict.empty
                or not timetable_conflict.empty
            ):

                st.error(
                    "Sorry. This classroom is no longer "
                    "available for the selected time. "
                    "Please choose another classroom."
                )


            # ------------------------------------------------
            # CREATE BOOKING
            # ------------------------------------------------

            else:

                booking_numbers = (
                    current_bookings["booking_id"]
                    .astype(str)
                    .str.extract(
                        r"(\d+)",
                        expand=False
                    )
                    .astype(int)
                )


                next_number = (
                    booking_numbers.max() + 1
                )


                new_booking_id = (
                    f"B{next_number:04d}"
                )


                new_booking = pd.DataFrame(
                    [
                        {
                            "booking_id": new_booking_id,
                            "student_id": int(
                                student["student_id"]
                            ),
                            "room_id": selected_room,
                            "date": requested_date,
                            "start_time": requested_start,
                            "end_time": requested_end,
                            "activity": activity,
                            "status": "Confirmed"
                        }
                    ]
                )


                # ------------------------------------------------
                # SAVE
                # ------------------------------------------------

                new_booking.to_csv(
                    bookings_file,
                    mode="a",
                    header=False,
                    index=False
                )


                # ------------------------------------------------
                # CONFIRMATION
                # ------------------------------------------------

                st.balloons()

                st.success(
                    "🎉 Classroom Booking Confirmed!"
                )

                st.subheader(
                    f"Booking ID: {new_booking_id}"
                )

                st.write(
                    f"**Student:** {student['name']}"
                )

                st.write(
                    f"**Student ID:** {student['student_id']}"
                )

                st.write(
                    f"**Department:** {student_department}"
                )

                st.write(
                    f"**Classroom:** {selected_room}"
                )

                st.write(
                    f"**Date:** {requested_date}"
                )

                st.write(
                    f"**Time:** {requested_start} - "
                    f"{requested_end}"
                )

                st.write(
                    f"**Activity:** {activity}"
                )

                st.write(
                    f"**Number of Students:** {student_count}"
                )

                st.write(
                    f"**Location:** "
                    f"{selected_room_data['building']}"
                )