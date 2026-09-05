# universal_kholloscopeur
Un projet de conversion intelligente de csv sous un format importable sur todoist à partir d'un calendrier


# Pour l'exécution 

La première chose à faire est de s'assurer que le fichier excel (ou le pdf qui sera converti en tableau excel) respect les conditions décrites dans la section ci-dessous. <br>

## 1) Conditions sur le fichier excel :

Si le kholloscope est de la forme suivante (informations en trop), il faut les supprimer avant export en CSV :

<p>
  <img src="Images/Kholloscope%2Bbruit.png" width="500">
  <img src="Images/kholloscope_sans_bruit.png" width="500">
</p>

- Toutes les catégories doivent être à minima séparées par un espace. Par exemple, dans une cellule :
  - Lundi 12h00 : OK
  - Lundi-12h00 : NON (sera considéré comme un mot, échouera les tests de catégories)
- Les salles sont inscrites dans une cellule à part (une cellule contenant "lundi d300" aura pour valeur de salle "lundi d300")
- Idem pour le professeur
- Les semaines du kholloscope doivent contenir dans la même case une information au moins sur le jour mais aussi sur le mois (e.g. "02/01" ou même "2-sept") mais surtout pas comme dans l'exemple suivant :

![eleves_semaines_confondus.png](Images/eleves_semaines_confondus.png)
Ici les semaines ne peuvent être ditinguées des élèves dans un format CSV, on peut alors rajouter le mois manuellement :

![version_corrigee.png](Images/version_corrigee.png)
Et ici le code fonctionnera parfaitement.

## Exemples de tableurs fonctionnels (se rapprocher de leurs formats peut résoudre des problèmes)

![basique.png](Images/basique.png)
![version_corrigee.png](Images/version_corrigee.png)
![kholloscope_sans_bruit.png](Images/kholloscope_sans_bruit.png)


## 2) Convertir le tableau en CSV

Cela se fait simplement depuis le tableur ("enregistrer sous" ou "exporter", choisir le format CSV)


## 3) S'approprier le code

1. Il faut disposer de python 3.8 ou plus
2. Il faut avoir un IDE (ex : PyCharm, Visual Studio Code, etc.)
3. Il faut installer la librairie pandas (version ≥ 2.1)




## Dépendances :

- pandas >= 2.1

https://www.todoist.com/help/articles/import-or-export-a-project-as-a-csv-file-in-todoist-YC8YvN#h_01JR212YPZY4QYZKGKARRSSSRZ

Si vous avez la moindre suggestion, le moindre bug, essayez d'ouvrir un ticket sur github ou de me contacter par mail :
universalkholloscopeur.support@gmail.com