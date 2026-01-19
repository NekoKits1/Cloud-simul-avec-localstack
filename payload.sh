#!/bin/bash

IMAGE_B64=$(base64 -w 0 black_hole1.jpg)
filename="black_hole1.jpg"

echo "... Création du payload JSON..."
cat > test_event.json << EOF
{
  "image": "$IMAGE_B64",
  "filename": "$filename",
  "user_id": "kitis"
}
EOF
