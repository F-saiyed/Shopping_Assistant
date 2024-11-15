# Shopping_Assistant
The Shopping Assistance Chatbot is designed to provide users with an interactive shopping experience by leveraging natural language processing. It utilizes OpenAI's GPT-4 to handle queries, product searches, and recommendations, along with cart management. Built with Flask, this chatbot allows users to interact through a web-based interface to make shopping assistance more efficient and user-friendly.

# Setup Instructions:

1.	Clone the Repository:
git clone <https://github.com/F-saiyed/Shopping_Assistant.git>
cd <repository-name>

2.	Create a Virtual Environment:
** For Windows**
python -m venv venv

** For macOS/Linux**
python3 -m venv venv

3.	Activate the virtual environment:
**  For Windows**
venv\Scripts\activate

**  For macOS/Linux**
source venv/bin/activate

4.	Install Dependencies:
pip install -r requirements.txt
pip install flask openai python-dotenv # to manually install the dependencies

5.	Set OpenAI API Key:
OPENAI_API_KEY=your_openai_api_key_here

6.	Running via Flask Web App:
python app.py
export FLASK_APP=app.py # For macOS/Linux
set FLASK_APP=app.py     # For Windows
http://127.0.0.1:5000


