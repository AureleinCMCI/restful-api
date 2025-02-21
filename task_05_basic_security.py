from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity)
import datetime

app = Flask(__name__)

# Clé secrète pour signer les tokens JWT
app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'  # La clé secrète pour signer le JWT
jwt = JWTManager(app)  # Initialisation de JWTManager

auth = HTTPBasicAuth()

# Liste des utilisateurs avec mots de passe hashés et rôles
users = {
    "john": {
        "password": generate_password_hash("hello"),
        "role": "user"
    },
    "admin": {
        "password": generate_password_hash("admin123"),
        "role": "admin"
    }
}

# Vérification du mot de passe avec Basic Auth
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]["password"], password):
        return username  # Retourne l'utilisateur authentifié

# Route protégée avec Basic Auth
@app.route('/protected_basic', methods=["GET"])
@auth.login_required  # Protégé avec Basic Auth
def protected_basic():
    return jsonify({"message": f"Bienvenue, {auth.current_user()} avec Basic Auth !"})

# Route publique (sans authentification)
@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API !"})

# Fonction pour créer un token JWT
def create_jwt_token(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Le jeton expire après 1 heure
    role = users[username]["role"]
    payload = {
        'sub': username,
        'exp': expiration,
        'role': role  # Ajoute le rôle de l'utilisateur dans le payload
    }
    token = create_access_token(identity=username, additional_claims={'role': role})  # Créer un token avec le rôle
    return token

# Route pour se connecter et obtenir un JWT
@app.route('/login', methods=["POST"])
def login():
    # Récupérer les identifiants dans la requête
    username = request.json.get("username")
    password = request.json.get("password")
    
    # Vérifier les identifiants
    if username in users and check_password_hash(users[username]["password"], password):
        token = create_jwt_token(username)  # Créer un token JWT avec le rôle
        return jsonify({"token": token})  # Retourner le jeton JWT
    else:
        return jsonify({"message": "Identifiants invalides"}), 401

# Route protégée avec JWT
@app.route('/jwt-protected')
@jwt_required()
def jwt_protected():
    return jsonify({"message": "JWT Auth: Access Granted"})

# Route protégée pour les utilisateurs "admin"
@app.route('/admin-only')
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()  # Récupérer l'identifiant de l'utilisateur
    role = get_jwt_identity()['role']  # Récupérer le rôle de l'utilisateur depuis le JWT

    if role != 'admin':  # Vérifier que l'utilisateur a le rôle admin
        return jsonify({"error": "Admin access required"}), 403

    return jsonify({"message": "Admin Access: Granted"})

# Gérer les erreurs de token
@jwt.unauthorized_loader
def handle_unauthorized_error(err):
    return jsonify({"error": "Missing or invalid token"}), 401

@jwt.invalid_token_loader
def handle_invalid_token_error(err):
    return jsonify({"error": "Invalid token"}), 401

@jwt.expired_token_loader
def handle_expired_token_error(err):
    return jsonify({"error": "Token has expired"}), 401

@jwt.revoked_token_loader
def handle_revoked_token_error(err):
    return jsonify({"error": "Token has been revoked"}), 401

@jwt.needs_fresh_token_loader
def handle_needs_fresh_token_error(err):
    return jsonify({"error": "Fresh token required"}), 401

if __name__ == '__main__':
    app.run(debug=True)
