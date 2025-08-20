# Smart EV Routing App

**Team - Mind_Mesh**  
**Developers**: Amrutha D, Vishnu V  
**Institution**: REVA University, Bangalore

---

## 🚀 Live Demo  
[Click here to try the app](https://smart-ev-routing-app.streamlit.app/)

## 💻 GitHub Repository  
[https://github.com/vishnuv336699/Smart-EV-Routing-App](https://github.com/vishnuv336699/Smart-EV-Routing-App)

---

## 🧠 Problem Statement  
**[Fleet Operations] Problem-2.1: EV Routing with Multi-Service Delivery Model**

---

## ✨ Features

- 📂 Upload custom test cases or use built-in ones
- 🗺️ Visualize vehicle routes on an interactive map
- ⚙️ Optimize deliveries using Google OR-Tools
- ⚡ Smart Discharge Mode for grid-aware energy return
- 📊 Real-time display of energy usage, earnings, and driver scores

---

## ⚙️ Requirements

Install the required libraries:


pip install -r requirements.txt


---

## 🛠️ How to Run the App Locally (VS Code)

### 1. Clone the Repository


git clone https://github.com/gv-2309/Smart-EV-Routing-App.git

cd Smart-EV-Routing-App


### 2. Create and Activate a Virtual Environment (Recommended)

bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate


### 3. Install Dependencies


pip install -r requirements.txt


---

## 📁 Ensure Folder Structure

Place your CSV test cases inside a folder named `Test_Case_CSV_Files` in the project directory.

### Example Structure:

```
Smart-EV-Routing-App/
├── streamlit_app.py
├── requirements.txt
├── Test_Case_CSV_Files/
│   ├── Bangalore_testcase.csv
│   ├── Kolkata_testcase.csv
│   ├── Delhi_testcase.csv
│   ├── Mumbai_testcase.csv
│   ├── Hyderabad_testcase.csv
│   └── Chennai_testcase.csv
```

---

## 📥 Sample Input Format

CSV file **must contain** the following columns:

* `ID`
* `Latitude`
* `Longitude`
* `Demand`
* `NodeType` (Depot, Customer, DischargeStation)
* `Location`

---

## 📽️ Demo Video

🎬 [Watch Demo](https://tinyurl.com/hackotsav-2k25)

---

## 📬 Contact

For queries or collaboration, reach out:

* Vishnu V — [vishnuv336699@email.com](mailto:vishnuv336699@email.com)
* Amrutha D — [amruthadandigimath@gmail.com](mailto:amruthadandigimath@gmail.com)

```



