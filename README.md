# **Fake News Detection**  

## 📌 **Overview**  
This project aims to detect fake news articles using Machine Learning. It classifies news as **Real** or **Fake** based on textual content. The application is built with **Flask** for the web interface and utilizes a trained model for predictions.  

## 📂 **Project Structure**  
- **`app.py`** – Flask backend to handle predictions.  
- **`vectorizer.pkl`** – Pre-trained ML model for fake news classification.
 - **`fake_news_detection.pkl`** – Pre-trained ML model for fake news classification.  
- **`templates/`** – HTML files for the web interface.  
- **`requirements.txt`** – List of dependencies.  
- **`report.pdf`** – Documentation and analysis of the project.  

## 🛠 **Technologies Used**  
- **Python** (Flask, Pandas, Scikit-learn)  
- **Machine Learning** (TF-IDF, Naïve Bayes, or any other classifier used)  
- **HTML, CSS, JavaScript** for UI  

## 🚀 **How to Run**  
1. Clone the repository:  
   ```sh
   git clone https://github.com/yourusername/Fake-News-Detection.git
   cd Fake-News-Detection
   ```
2. Install dependencies:  
   ```sh
   pip install -r requirements.txt
   ```
3. Run the Flask app:  
   ```sh
   python app.py
   ```
4. Open in browser:  
   ```
   http://127.0.0.1:5000/
   ```

## 📈 **Future Enhancements**  
- Improve model accuracy with deep learning.  
- Deploy the app on cloud platforms (Heroku, AWS, etc.).  
- Add a user feedback system for continuous improvement.  

