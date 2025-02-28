from flask import Flask, render_template, request, send_from_directory,jsonify
import random, os
from werkzeug.utils import secure_filename
from functions import img_predict, get_diseases_classes, get_crop_recommendation, get_fertilizer_recommendation, soil_types, Crop_types, crop_list
from flask_mail import Mail, Message
from datetime import datetime


app = Flask(__name__)
random.seed(0)
app.config['SECRET_KEY'] = os.urandom(24)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
	if request.method == "POST":
		to_predict_list = request.form.to_dict()
		to_predict_list = list(to_predict_list.values())
		to_predict_list = list(map(float, to_predict_list))
		result = get_crop_recommendation(to_predict_list)
		return render_template("recommend_result.html", result=result)
	else:
		return render_template('crop-recommend.html')

@app.route('/fertilizer-recommendation', methods=['GET', 'POST'])
def fertilizer_recommendation():
	if request.method == "POST":
		to_predict_list = request.form.to_dict()
		to_predict_list = list(to_predict_list.values())
		to_predict_list = list(map(float, to_predict_list))
		result = get_fertilizer_recommendation(
			num_features=to_predict_list[:-2],
			cat_features=to_predict_list[-2:]
		)
		return render_template("recommend_result.html", result=result)
	else:
		return render_template(
			'fertilizer-recommend.html', 
			soil_types=enumerate(soil_types),
			crop_types=enumerate(Crop_types)
		)

	
@app.route('/crop-disease', methods=['POST','GET'])
def find_crop_disease():
	if request.method=="GET":
		return render_template('crop-disease.html', crops=crop_list)
	else:
		file = request.files["file"]
		crop = request.form["crop"]

		basepath = os.path.dirname(__file__)
		file_path = os.path.join(basepath,'uploads',  secure_filename(file.filename))
		file.save(file_path)
		prediction = img_predict(file_path, crop)
		result = get_diseases_classes(crop, prediction)

		return render_template('disease-prediction-result.html', image_file_name=file.filename, result=result,crop=crop)

@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)
@app.route('/weather', methods=['GET'])
def weather():
	return render_template('weather.html')

@app.route('/feedback', methods=['GET'])
def feedback():
	return render_template('feed_back.html')



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vynipersonal@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ncdqfjrzzbwyqbtz'  # Replace with your email password or app password
app.config['MAIL_DEFAULT_SENDER'] = 'vynipersonal@gmail.com'  # Replace with your email
app.config['MAIL_USE_SSL'] = False 
mail = Mail(app)

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning 🌞"
    elif hour < 18:
        return "Good Afternoon 🌾"
    else:
        return "Good Evening 🌙"

  # Update with your HTML file name

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json  # Parse JSON data
        email = data.get('email')  # Extract email
        print(email)
 
        if not email:
            return jsonify({'error': 'Email is required!'}), 400

        # Compose email content
        greeting = get_greeting()
        subject = "Welcome to Weather Updates 🌦️"
        body = f"""
{greeting},

We are thrilled to welcome you to our Weather Updates community! 🌤️🌧️

With your subscription, you will receive the latest and most accurate weather forecasts, alerts, and insights to help you plan your days effectively. Stay informed about weather patterns, seasonal changes, and tips to stay safe and prepared.

Thank you for placing your trust in us. We’re here to keep you updated and well-informed, rain or shine! 🌞

If you have any questions or suggestions, feel free to reach out to us at any time.

Best regards,  
The Weather Updates Team
DemeterAI
"""

        # Send email
        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)

        return jsonify({'message': 'Subscription successful! Email sent.'}), 200
    except Exception as e:
        print(e)  # Log the error for debugging
        return jsonify({'error': 'Failed to send email.'}), 500


	
if __name__ == '__main__':
	app.run(debug=True)