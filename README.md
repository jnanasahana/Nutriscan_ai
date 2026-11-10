NutriScan-AI – Smart Food Analyzer & Health Advisor

Project Overview

NutriScan-AI is a smart food analysis application designed to help users understand the nutritional information and potential health impact of packaged food products.

The application uses Optical Character Recognition (OCR) to extract ingredient information from uploaded food product images. It analyses the extracted ingredients and provides health-related insights, warnings and recommendations.

The main goal is to help users make more informed food choices.

Problem Statement

Many people find it difficult to understand food labels and identify ingredients that may affect their health. Reading long ingredient lists and identifying potentially harmful additives can be challenging.

NutriScan-AI aims to simplify this process by automatically extracting ingredient information and presenting easy-to-understand health insights.

Technologies Used

- **Programming Language:** Python
- **Backend Framework:** Flask
- **OCR Technology:** Tesseract OCR
- **Image Processing:** Pillow (PIL)
- **Database:** SQLite
- **Database Management:** Flask-SQLAlchemy
- **Authentication:** Flask-Login
- **Deep Learning / Machine Learning Libraries:** TensorFlow, Scikit-learn
- **Data Processing:** NumPy, Pandas
- **Development Tools:** Visual Studio Code, Git, GitHub

Key Features

1. **User Registration and Login:** Provides user authentication and secure password hashing.

2. **Food Image Upload:** Allows users to upload packaged food images in supported formats such as JPG and PNG.

3. **Ingredient Extraction:** Uses Tesseract OCR to extract ingredient text from uploaded food product images.

4. **Ingredient Analysis:** Identifies ingredients and categorises their potential health impact.

5. **Health Insights and Warnings:** Provides information about ingredients that may require attention.

6. **Nutrition Dashboard:** Displays food analysis information and health-related insights.

7. **Nutrition History:** Provides access to previous food analysis information.

8. **Diet Goals and Recommendations:** Helps users understand possible improvements to their food choices.

Project Structure

text
Nutriscan_ai/
│
├── app.py
├── analysis.py
├── ocr.py
├── parse.py
├── init.py
├── requirements.txt
│
├── base.html
├── login.html
├── Settings.html
├── dashboard.html
├── diet_goals.html
├── health_insights.html
├── nutrition_history.html
├── profile.html
├── result.html
│
├── sample_ingredients.csv
├── sample_ocr_text.txt
│
├── README.md
└── .gitignore

Installation Instructions

Follow these steps to run the project locally.

1. Clone the Repository

bash
git clone https://github.com/jnanasahana/Nutriscan_ai.git


2. Navigate to the Project Folder

bash
cd Nutriscan_ai

3. Create a Virtual Environment

bash
python -m venv venv

Activate the environment:

**Windows:**
bash
venv\Scripts\activate

4. Install Required Dependencies

bash
pip install -r requirements.txt

5. Install Tesseract OCR

Install Tesseract OCR on your system and configure its executable path if it is not automatically detected by Python.

6. Configure Environment Variables

Create a local .env file and configure the required application settings.

Example:
env
FLASK_SECRET=your_secure_random_secret

Do not upload your actual .env file or secret credentials to GitHub.

7. Run the Application

bash
python app.py

Open the application in your browser:

text
http://127.0.0.1:5000

Screenshots

Add screenshots of the application here.

Recommended screenshots:

- Login and Registration Page
- Nutrition Dashboard
- Food Image Upload Page
- Food Analysis Results
- Health Insights Page

Store your screenshots inside a screenshots/ folder and display them using Markdown image links.

Example:

markdown
![Dashboard](screenshots/dashboard.png)

Future Enhancements

- Improve ingredient recognition accuracy.
- Enhance deep learning-based food analysis.
- Add more comprehensive nutritional information.
- Provide personalised dietary recommendations.
- Improve the user interface and dashboard.
- Expand the ingredient database.
- Add support for multiple languages.

Author

**Jnana Jyothi T S**

B.E. Computer Science and Engineering (Data Science) Graduate

## Connect With Me

- **GitHub:** https://github.com/jnanasahana
- **LinkedIn:** https://www.linkedin.com/in/jnana-jyothi-t-s-0a142027a

---

*NutriScan-AI – Making smarter food choices easier through technology.*
