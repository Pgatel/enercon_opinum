# enercon_opinum

Mise à jour de la data base Opinum avec la production électrique des éoliennes Enercon.

Le programme utilise la connexion vers le SCADA de chaque éolienne au travers du VPN d'Enercon
pour aller lire les valeurs instantanées de production. Parmi celles-ci, on utilise la
production totale. Par différence avec la dernière valeur enregistrée, on a la production
sur la période depuis le dernier lancement du programme.

Le programme est lancé toutes les 10 minutes afin d'être conforme au SCADA. Le programme 
tourne sur un serveur VPS (Hostinger). 

La liste des éoliennes à interroger se trouve dans le fichier INI "wind_turbines.ini" qui
se trouve dans la racine.

Le programme est configuré dans Github.