import requests
import csv

# Fonction pour récupérer et afficher les posts
def fetch_and_print_posts():
    response = requests.get('https://jsonplaceholder.typicode.com/posts')
    print("Status Code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        for post in data:
            print(post['title'])
    else:
        print("Request failed!")

# Fonction pour récupérer, structurer et sauvegarder les posts dans un CSV
def fetch_and_save_posts():
    response = requests.get('https://jsonplaceholder.typicode.com/posts')
    
    if response.status_code == 200:
        data = response.json()
        
        structured_data = []
        for post in data:
            structured_data.append({
                "id": post['id'],
                "title": post['title'],
                "body": post['body']
            })
        
        # Écrire les données dans un fichier CSV
        with open('posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'body']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()  # Écrire l'en-tête
            writer.writerows(structured_data)  # Écrire les données
        
        print("Posts saved to posts.csv successfully!")
    else:
        print("Request failed!")

