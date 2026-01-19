import json  # permet de manipuler les requêtes et les réponses HTTP
import base64  # permet de convertir les fichiers binaires brutes en chaînes de caractères compréhensibles pour le format JSON ou les URLs
import boto3  # permet d'utiliser tous les services AWS directement, sans passer par aws cli
import uuid  # permet de générer des id uniques pour chaque photo
from PIL import Image  # permet le redimensionnement
from io import BytesIO  # permet de manipuler les données en mémoire RAM
from datetime import datetime  # pour avoir la date d'upload

# Connexion à DynamoDB et au bucket
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client("s3", region_name="us-east-1")
table = dynamodb.Table("Photos")
BUCKET_NAME = "bucket-images"


def lambda_handler(event, context):
    try:
        # 1. Extraire les données de l'image upload
        body = json.loads(event.get('body', '{}'))  # charger les requêtes entrantes dans event["body"]
        image_base64 = body.get('image')  # récupère l'image encodée en base64
        filename = body.get('filename', 'image.jpg')
        user_id = body.get('user_id', 'anonymous')

        # Vérification de l'existence de l'image
        if not image_base64:
            return {
                'statusCode': 400,  # erreur niveau client
                'body': json.dumps({'error': 'Image manquante'})
            }

        # 2. Décoder l’image (texte base64 → données binaires)
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))  # crée un fichier en mémoire RAM et l'ouvre

        # 3. Générer un identifiant unique pour la photo
        timestamp = datetime.utcnow()
        upload_date_iso = timestamp.isoformat() + 'Z'
        photo_id = f"{timestamp.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4()}"
        extension = filename.split('.')[-1].lower()  # récupère l'extension du fichier
        base_filename = f"photo_{photo_id}.{extension}"  # nom final du fichier

        # MIME type correct
        mime_types = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'
        }
        content_type = mime_types.get(extension, 'image/jpeg')

        # 4. Obtenir les dimensions originales
        original_width, original_height = image.size  # les dimensions
        original_size = len(image_bytes)  # la taille en octets

        # 5. Créer les différentes tailles
        sizes = {
            'original': image,
            'medium': resize_image(image, 800, 600),
            'thumbnail': resize_image(image, 150, 150)
        }

        # 6. Upload de l’image dans S3
        s3_urls = {}  # création d'un dictionnaire pour les chemins S3
        for size_name, img in sizes.items():  # pour chaque version de l'image
            s3_key = f"images/{size_name}/{base_filename}"
            # convertir l'image en bits
            buffer = BytesIO()  # réservation d'espace mémoire
            save_format = img.format if img.format else 'JPEG'
            img.save(buffer, format=save_format)
            buffer.seek(0)  # remise du curseur au début du fichier (étape obligatoire)

            # upload
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=buffer.getvalue(),
                ContentType=content_type
            )
            s3_urls[size_name] = f"s3://{BUCKET_NAME}/{s3_key}"

        # 7. Enregistrer les métadonnées dans DynamoDB
        table.put_item(Item={
            'user_id': user_id,
            'photo_id': photo_id,
            'filename': filename,
            'upload_date': upload_date_iso,
            'metadata': {
                'original_size': original_size,
                'width': original_width,
                'height': original_height,
                's3_urls': s3_urls
            }
        })

        # 8. Retourner la réponse de succès
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Photo uploadée avec succès',
                'photo_id': photo_id,
                'urls': s3_urls,
                'metadata': {
                    'width': original_width,
                    'height': original_height,
                    'size': original_size,
                    'upload_date': upload_date_iso
                }
            })
        }

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Erreur lors du traitement',
                'details': str(e)
            })
        }


# Fonction pour redimensionner l'image
def resize_image(image, max_width, max_height):
    # Créer une copie pour ne pas modifier l'original
    img = image.copy()
    # Calculer les nouvelles dimensions en conservant le ratio
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return img
