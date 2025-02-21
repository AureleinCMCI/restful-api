from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity)
import datetime

# Initialiser l'application Flask
app = Flask(__name__)

# Configurer la clé secrète pour signer les tokens JWT
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Utilisez une clé secrète robuste en production
jwt = JWTManager(app)

# Initialiser l'authentification de base
auth = HTTPBasicAuth()

# Liste des utilisateurs avec mots de passe hashés et rôles
users = {
    "user1": {"username": "user1", "password": generate_password_hash("password"), "role": "user"},
    "admin1": {"username": "admin1", "password": generate_password_hash("password"), "role": "admin"}
}

# Vérification du mot de passe avec Basic Auth
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]["password"], password):
        return username  # Authentification réussie

# Fonction pour créer un token JWT
def create_jwt_token(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Le token expire après 1 heure
    user_data = users[username]
    payload = {
        'sub': username,
        'role': user_data["role"],  # Ajout du rôle dans le payload du JWT
        'exp': expiration
    }
    token = create_access_token(identity=username, additional_claims={"role": user_data["role"]})  # Création du JWT
    return token

# Route pour accéder à une ressource protégée avec l'authentification de base
@app.route('/basic-protected', methods=["GET"])
@auth.login_required  # Protéger avec l'authentification de base
def basic_protected():
    return jsonify({"message": "Basic Auth: Access Granted"})

# Route publique (sans authentification)
@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API !"})

# Route pour se connecter et obtenir un JWT
@app.route('/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    # Vérification des identifiants
    if username in users and check_password_hash(users[username]["password"], password):
        token = create_jwt_token(username)  # Créer un token JWT
        return jsonify({"access_token": token})  # Retourner le token JWT
    else:
        return jsonify({"message": "Identifiants invalides"}), 401

# Route protégée par JWT
@app.route('/jwt-protected', methods=["GET"])
@jwt_required()  # Protéger avec un token JWT
def jwt_protected():
    return jsonify({"message": "JWT Auth: Access Granted"})

# Route uniquement accessible aux administrateurs (Role-based Access Control)
@app.route('/admin-only', methods=["GET"])
@jwt_required()  # Protéger avec un token JWT
def admin_only():
    current_user = get_jwt_identity()
    user_role = current_user["role"]

    # Vérifier si l'utilisateur a le rôle "admin"
    if user_role != "admin":
        return jsonify({"error": "Admin access required"}), 403  # Accès refusé si ce n'est pas un admin

    return jsonify({"message": "Admin Access: Granted"})

# Gestion des erreurs liées au JWT
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

# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
