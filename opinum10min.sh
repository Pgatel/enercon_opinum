#!/bin/bash

# Horodatage du démarrage
echo "Enercon_opinum starting at $(date)"

cd /home/pascal/enercon_opinum || exit

# Commande VPN (commentée ici, assurez-vous qu'elle fonctionne si activée)
# openconnect -q -b -u wf-08916-001 sslvpn2.enercon.de < pass.txt

# Définir les noms des fichiers de log
logfile="enercon_opinum_$(date '+%Y%m%d').log"

# Exécuter le script Python et capturer les erreurs
/home/pascal/eolelien_env/bin/python enercon_opinum.py debug >> "$logfile" 2>&1

# Horodatage de la fin
echo "Enercon_opinum ending at $(date)"
