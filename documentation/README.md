# EngageWise

## 1. **Project Title and Overview**  
EngageWise is a real-time focus monitoring and productivity-enhancing system designed to help users maintain attention during work or study sessions. By leveraging computer vision techniques such as facial movement analysis, eye tracking, and blink/yawn detection, EngageWise provides timely feedback to mitigate distractions and boost productivity. The system employs OpenCV and dlib for facial landmark detection. A Privacy-by-Design approach ensures user data remains secure, with all processing conducted locally on the user's device. 

---

## 2. **Repository Contents**  

| **Folder Name**       | **Description**                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------|
| **`src/`**        | Contains core system code, including the main entry point (`app.py`), models, utilities, etc. |
| **`deployment/`**   | Houses containerization and CI/CD configuration files, including the `Dockerfile`.            |
| **`metrics/`**      | Evaluation and performance metric-related scripts, including `evaluation.py`.                 |
| **`documentation/`**| Templates, reports, and documentation tracking the project lifecycle.                         |
| **`videos/`**       | Contains demo screencasts showcasing the system in action.                                    |

---

## 3. **System Entry Point**  
- **Main Script:** `src/app.py`  
- **Running Locally:**
  ```python
  python -m streamlit run src/app.py
  ```

## 4. **Video Demonstration**
A demo video showcasing system deployment, backend processing, and metrics monitoring can be found in the `videos/` folder. It highlights the end-to-end deployment strategy and system performance.

## 5. **Deployment Strategy**
The system is deployed using Streamlit, which provides a simple and effective way to deploy and share data applications.

**Instructions for Local Deployment:**
- Install the required dependencies: Make sure you have all the necessary Python libraries installed. If not, you can install them using:
```python
pip install -r src/requirements.txt
```
- Run the Streamlit app locally:
```python
python -m streamlit run src/app.py
```
The application will be available at `http://localhost:8501`

## 6. **Monitoring and Metrics**  
The system includes built-in monitoring to track performance and user feedback.

- **Frame Rate Latency Tracking:**  
  The app tracks and reports the average latency (frame rate) of the system during usage. This metric helps assess the real-time responsiveness of the application.

- **User Feedback:**  
  The UI/UX of the app has a feedback mechanism where users can submit their experience and rate system performance. This feedback is stored in the `user_feedback.csv` file and used for monitoring and improving the app's performance.

- **Session Data:**  
  The app also logs session-related data in the `session.csv` file, which tracks usage metrics and overall system performance during user interactions.

- **Metrics Overview:**  
  - **Frame Rate Latency:** Average frame rate over time.
  - **User Feedback:** Collected ratings and comments stored in `user_feedback.csv`.
  - **Session Data:** Logged session performance in `session.csv`.

These metrics are key to understanding both system efficiency and user satisfaction. All data is logged for ongoing performance evaluation and optimization.

## 7. **Project Documentation**
- **AI System Project Proposal**: `documentation/EngageWise Project Plan.docx`
- **Project Report**: `documentation/Paper.docx`

## 8. **Version Control and Team Collaboration**  
- **Version Control Practices:**  
  - **Branching Strategy:** The `main` branch is used as the only branch for stable releases. Development work is done in separate folders for each team member within the repository.
  - **Code Reviews:** All pull requests are reviewed before merging to ensure code quality and consistency.

- **Collaboration Tools:**  
  - GitHub Projects/Issues are used for tracking tasks, progress, and team contributions, ensuring smooth collaboration and task management.

## 9. **If Not Applicable**
- **Docker**: While the application runs smoothly in a local Conda environment for Streamlit, we encountered dependency conflicts when attempting to build a Docker image. Due to these incompatibilities and since the application consists of a single component, containerization was deemed unnecessary. As a result, we opted to deploy the app locally using Streamlit's built-in localhost functionality.

```bash
=> ERROR [4/4] RUN pip install --no-cache-dir -r src/requirements.txt
> [4/4] RUN pip install --no-cache-dir -r src/requirements.txt: 35.43 ERROR: dlib-19.22.99-cp39-cp39-win_amd64.whl is not a supported wheel on this platform.
```
- **Prometheus/Grafana**: Due to limited experience in these areas and time constraints, we have resorted to hardcoding the monitoring techniques.

