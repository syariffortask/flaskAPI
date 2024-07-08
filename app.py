from flask import Flask,request,jsonify,url_for,send_from_directory
from model import db
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = './image'  # Replace with your upload folder path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB maximum file size


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:superadmin@localhost/sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Inisialisasi SQLAlchemy
db.init_app(app)

# Inisialisasi Flask-Migrate
migrate = Migrate(app,db)

from model import User,Counter

# Dapatkan konteks aplikasi sebelum melakukan operasi SQLAlchemy
with app.app_context():
    # Create the database tables
    db.create_all()


# Routes

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    # If user does not select file, browser also submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File successfully uploaded', 'filename': filename}), 201
    else:
        return jsonify({'error': 'Allowed file types are png, jpg, jpeg'}), 400
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files', methods=['GET'])
def get_uploaded_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_list = [f for f in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return jsonify({'files': file_list}), 200

@app.route('/display/<filename>')
def display_image(filename):
    return f'<img src="{url_for("uploaded_file", filename=filename)}" alt="{filename}">'

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'username': user.username,'id': user.id, 'email': user.email,'password':user.password} for user in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@app.route('/users', methods=['POST'])
def create_user():
    
    if not request.json:
        return jsonify({"message":"Request body harus JSON"}),400
    
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} harus diisi"}), 400
    
    usr_name = data['username']
    email = data['email']
    password = data['password']
    if not usr_name or not email or not password:
        return(
            jsonify({"message":"username,password,email harus di isi"}),400,
        )
    
    existing_user = User.query.filter((User.username == usr_name) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "username atau email sudah terdaftar"}), 400
    
    new_user = User(username=usr_name,password=password, email=email)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': str(e)}),500
    return jsonify({'message': 'User created successfully!'}),201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']
    db.session.commit()
    return jsonify({'message': 'User updated successfully!'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully!'})

@app.route('/counter',methods=['GET'])
def get_counters():
    counts = Counter.query.all()
    return jsonify([{'id': count.id, 'lokasi': count.lokasi, 'jenis': count.jenis,'track_id':count.track_id,'Waktu':count.waktu} for count in counts])

@app.route('/counter/<int:id>',methods=['GET'])
def get_counter(id):
    counter = Counter.query.get_or_404(id)
    return jsonify({'id':counter.id,'jenis':counter.jenis,'lokasi':counter.lokasi,'waktu':counter.waktu,'track_id':counter.track_id})


@app.route('/counter',methods=['POST'])
def insert_counter():
    if not request.json:
        return jsonify({'message': 'Request body harus JSON'}), 400
    
    required_field=['lokasi','jenis','track_id']
    for field in required_field:
        if field not in request.json:
            return jsonify({'message': f'Field {field} harus di isi'}), 400
    
    data = request.get_json()
    jenis = data['jenis']
    lokasi = data['lokasi']
    track_id = data['track_id']
    
    if not lokasi or not track_id or not lokasi:
        return jsonify({'message': 'Field tidak boleh kosong'}), 400
    
    new_count = Counter(lokasi=lokasi,jenis=jenis,track_id=track_id)
    try:
        db.session.add(new_count)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': 'Error: ' + str(e)}), 500
    return jsonify({'message': 'Berhasil insert data count'}),201

@app.route('/counter/<int:id>', methods=['PUT'])
def update_counter(id):
    
    if not request.json:
        return jsonify({'message': 'Request body harus JSON'}), 400
    
    required_field=['lokasi','jenis','track_id']
    for field in required_field:
        if field not in request.json:
            return jsonify({'message': f'Field {field} harus di isi'}), 400
    
    
    
    counter = Counter.query.get_or_404(id)
    data = request.get_json()
    counter.jenis = data['jenis']
    counter.lokasi = data['lokasi']
    counter.track_id = data['track_id']
    db.session.commit()
    return jsonify({'message': 'Counter updated successfully!'})

@app.route('/counter/<int:id>', methods=['DELETE'])
def delete_counter(id):
    counter = Counter.query.get_or_404(id)
    db.session.delete(counter)
    db.session.commit()
    return jsonify({'message': 'COunter deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
