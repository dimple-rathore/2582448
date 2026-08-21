AI-Powered Classroom Allocation System



Problem Statement



Universities often have difficulty allocating classrooms efficiently because classroom capacity, available facilities, department location, timetable conflicts, and existing bookings must all be considered simultaneously.



This project develops a local AI-powered classroom allocation system that recommends suitable classrooms based on student requirements and helps prevent scheduling conflicts.



Objectives



\- Recommend suitable classrooms based on capacity and required facilities.

\- Consider the location of the student's department.

\- Check classroom availability using timetable information.

\- Prevent conflicting classroom bookings.

\- Provide an AI-generated explanation for classroom recommendations.

\- Maintain a local, privacy-friendly AI workflow without cloud APIs.



Features



\- Student login and authentication.

\- Department-based location preference.

\- Classroom recommendation and ranking.

\- Capacity suitability scoring.

\- Required facility filtering.

\- Near/Medium/Far location classification.

\- Timetable availability checking.

\- Booking conflict prevention.

\- Booking confirmation with unique booking ID.

\- Persistent booking records.

\- Local LLM-generated classroom explanations.

\- Streamlit-based interactive interface.



GenAI Components



Local Large Language Model



The project uses \*\*Gemma 3 1B through Ollama\*\*.



The LLM receives information about a recommended classroom, including:



\- Classroom ID

\- Building and floor

\- Capacity

\- Location category

\- Capacity score

\- Facility score

\- Required facilities



It then generates a short natural-language explanation of why the classroom is suitable.



The LLM runs locally through Ollama and does not require a cloud API.




Allocation Methodology



Classrooms are first filtered according to availability and required facilities.



The recommendation score combines three factors:



\*\*Overall Score = 0.50 × Capacity Score + 0.30 × Facility Score + 0.20 × Distance Score\*\*



Capacity Score



The capacity score measures how closely the classroom capacity matches the number of students.



Facility Score



The facility score evaluates whether the classroom provides the facilities requested by the user.



Distance Score



Department and classroom locations are classified as:



\- \*\*Near\*\* – same block

\- \*\*Medium\*\* – one block away

\- \*\*Far\*\* – more than one block away



Distance scores are:



\- Near = 100

\- Medium = 70

\- Far = 40



Dataset



The project uses locally generated synthetic data representing a university environment.



The generated dataset contains:



\- 200 students

\- 10 departments

\- 5 buildings

\- 300 classrooms

\- Timetable records

\- Existing booking records



The data is stored in CSV files under the `data/` directory.



Technologies Used



\- Python

\- Pandas

\- Streamlit

\- Ollama

\- Gemma 3 1B

\- Diffusers

\- Transformers

\- PyTorch

\- Git and GitHub




git clone https://github.com/dimple-rathore/2582448.git

cd 2582448

