#!/bin/bash
# Les 2 lignes suivantes sont à mettre dans crontab avec crontab -e
# Update Opinum database every 10 minutes with SCADA data
# */10 * * * * /home/pascal/enercon_opinum/opinum10min.sh >>/home/pascal/enercon_opinum/opinum10min.log 2>&1

# Horodatage du démarrage
echo "Enercon_opinum starting at $(date)"

cd /home/pascal/enercon_opinum || exit

# Le VPN vers enercon doit être ouvert (nécessairement lancé par root)
# openconnect -q -b -u wf-08916-001 sslvpn2.enercon.de < pass.txt

# Définir les noms des fichiers de log
logfile="enercon_opinum_$(date '+%Y%m%d').log"

# Exécuter le script Python et capturer les erreurs
/home/pascal/eolelien_env/bin/python enercon_opinum.py debug >> "$logfile" 2>&1

# Horodatage de la fin
echo "Enercon_opinum ending at $(date)"
