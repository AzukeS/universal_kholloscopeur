# universal_kholloscopeur
Un projet de conversion intelligente de csv sous un format importable sur todoist à partir d'un calendrier


# Pour l'exécution 

## Conditions sur le fichier excel :
- Toutes les catégories doivent être à minima séparées par un espace. Par exemple, dans une cellule :
  - Lundi 12h00 : OK
  - Lundi-12h00 : NON (sera considéré comme un mot, échouera les tests de catégories)
- Les salles sont inscrites dans une cellule à part (une cellule contenant "lundi d300" aura pour valeur de salle "lundi d300")
- Idem pour le professeur

1. Il faut installer la librairie pandas
2. Il faut spécifier le chemin du kholloscope dans le fichier config.py
