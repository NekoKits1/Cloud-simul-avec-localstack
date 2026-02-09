# Cloud-simulé-avec-localstack
Ceci est un projet où on expérimente les services Cloud mais non facturés, en mettant en place un prototype de traitement d'image(redimensionnement), basé sur les services comme S3, Lambda, API-Gateway et DynamoDB

on Travaille ici avec DOCKER et on utilisera donc ces commande :
- pour lancer le conteneur localstack: *docker run --name localstack -d -p 4566:4566 -p 4510-4559:4510-4559  -v /var/run/docker.sock:/var/run/docker.sock -v localstack-data:/var/lib/localstack localstack/localstack*
- Pour utiliser la bibliotheque Pillow pour les redimensionnements de l'image: *docker run --rm -v "$PWD":/var/task --entrypoint /bin/bash public.ecr.aws/lambda/python:3.9 -c "pip install pillow -t package"*

# alice
Option 1 : Upload via script Bash (recommandé) 
Le fichier payload.sh simplifie l'upload d'images.
1. Rendre le script exécutable :
chmod +x payload.sh
2. Utiliser le script :
./payload.sh votre_image.jpg nom_utilisateur
Exemple :
./payload.sh photo_vacances.jpg alice

# Structure des fichiers
Cloud-simul-avec-localstack/
│
├── lambda_function.py      # Code de la fonction Lambda (traitement d'images)
├── payload.sh              # Script Bash pour upload facilité
├── README.md               # Ce fichier
│
└── package/                # Dépendances Python (Pillow) - à créer
    └── (fichiers Pillow)
