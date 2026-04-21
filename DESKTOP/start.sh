#!/bin/bash
echo "Installation des dépendances..."
pip3 install -r requirements.txt --quiet
echo ""
echo "Démarrage du serveur..."
python3 server.py
