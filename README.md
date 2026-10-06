# Simulation d'un Cloud Local avec LocalStack

Prototype serverless de traitement d'image (redimensionnement), construit pour expérimenter une architecture AWS événementielle **sans jamais payer un centime de facturation cloud réelle** — tout tourne en local via Docker et LocalStack.

> Projet académique. Le rapport complet est disponible dans `rapport.pdf`.

---

## Pipeline

```
┌──────────┐    upload     ┌────────────┐   trigger    ┌──────────┐
│  Client   │ ───────────► │  S3 bucket  │ ───────────► │  Lambda   │
│ (API REST)│               │  (source)   │               │ (resize)  │
└──────────┘               └────────────┘               └────┬─────┘
      ▲                                                        │
      │              ┌────────────┐                            │
      └───────────── │ API Gateway │ ◄── métadonnées ───────────┤
                      └────────────┘           │
                                          ┌─────▼──────┐
                                          │  DynamoDB   │
                                          │ (métadonnées)│
                                          └────────────┘
```

1. Le client dépose une image via une route exposée par **API Gateway**.
2. L'image atterrit dans un bucket **S3**, ce qui déclenche une fonction **Lambda**.
3. La Lambda redimensionne l'image et écrit le résultat dans un second bucket.
4. Les métadonnées (taille, format, horodatage) sont enregistrées dans **DynamoDB**.

Les quatre services sont orchestrés dans un seul environnement **Docker**, simulés localement par LocalStack — aucun compte AWS réel n'est nécessaire.

---

## Pourquoi LocalStack

Tester une architecture serverless sur AWS coûte de l'argent dès les premiers appels Lambda ou les premières requêtes API Gateway. LocalStack simule ces services en local avec la même API que AWS : le code écrit pour LocalStack fonctionne, à la configuration d'endpoint près, sur un vrai compte AWS.

---

## Stack technique

| Élément | Détail |
|---|---|
| Langage | Python |
| Services AWS simulés | S3, Lambda, DynamoDB, API Gateway |
| Orchestration | Docker / Docker Compose |
| Émulation cloud | LocalStack |

---

## Mise en place

**Prérequis** : Docker, Docker Compose, Python 3, [awscli-local](https://github.com/localstack/awscli-local) (`pip install awscli-local`).

```bash
# Démarrer LocalStack
docker compose up -d

# Créer le bucket source
awslocal s3 mb s3://images-source

# Déployer la fonction Lambda
awslocal lambda create-function \
  --function-name resize-image \
  --runtime python3.12 \
  --handler handler.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::000000000000:role/lambda-role

# Tester en déposant une image
awslocal s3 cp ./test.jpg s3://images-source/
```

---

## Ce que ce projet m'a appris

- Construire une architecture événementielle (S3 → Lambda → DynamoDB) sans dépendre d'un compte AWS facturé
- Déployer et invoquer une fonction Lambda via CLI
- Orchestrer plusieurs services cloud simulés dans un même environnement Docker
- Les limites de LocalStack par rapport à un vrai environnement AWS (latence, fidélité de certains services), utiles à connaître avant un passage en production
