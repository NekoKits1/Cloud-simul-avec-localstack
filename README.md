# Cloud-simul-avec-localstack
Ceci est un projet où on expérimente les services Cloud mais non facturés, en mettant en place un prototype de traitement d'image(redimensionnement), basé sur les services comme S3, Lambda, API-Gateway et DynamoDB

on Travaille ici avec DOCKER et on utilisera donc ces commande :
- pour lancer le conteneur localstack: sudo docker run --name localstack -d -p 4566:4566 -p 4510-4559:4510-4559  -v /var/run/docker.sock:/var/run/docker.sock -v localstack-data:/var/lib/localstack localstack/localstack
- Pour utiliser la bibliotheque Pillow pour les redimensionnements de l'image: docker run --rm -v "$PWD":/var/task --entrypoint /bin/bash public.ecr.aws/lambda/python:3.9 -c "pip install pillow -t package"
