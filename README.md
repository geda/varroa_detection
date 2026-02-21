# Varroa Detection

Détection et comptage automatique des varroas (*Varroa destructor*) dans des images de planches de ruches, à l'aide de la détection d'objets YOLOv11.

## Contexte

Le varroa destructor est un parasite qui infeste les colonies d'abeilles du monde entier. Il se fixe sur le corps des abeilles adultes, se reproduit dans les cellules operculées et transmet des virus affaiblissant le système immunitaire des abeilles. Sans traitement, les colonies s'effondrent en automne ou en hiver.

Après traitement à l'acide formique ou oxalique, les apiculteurs déposent une planchette sous la ruche pour évaluer le degré d'infestation. Les varroas morts tombent sur ce fond, mais leur petite taille (1–2 mm) et la présence de débris de cire rendent le comptage manuel fastidieux.

L'objectif de ce projet est de fournir un **ordre de grandeur automatique** du niveau d'infestation à partir d'une photo de la planche.

## Approche

- **Modèle de base :** modèle pré-entraîné issu de la publication MDPI (Yániz et al., Agriculture 2025, 15, 969), entraîné sur 357 images à haute résolution
- **Fine-tuning :** réentraînement sur un dataset personnel de 25 images (varroa-counter-large v5) hébergé sur [Roboflow](https://app.roboflow.com/varroa-counter/varroa-counter-large)
- **Classes détectées :** `varroa`, `goutte` (ajoutée en v5 pour réduire les faux positifs liés aux gouttes d'eau)
- **Format des données :** YOLOv11 (bounding boxes normalisées)

## Structure du projet

```
train_varroa.ipynb          # Notebook principal (Colab)
model_mdpi_3291496/
  weights/best.pt           # Poids du modèle pré-entraîné MDPI
runs/detect/
  train/                    # Métriques et poids du fine-tuning
  val*/                     # Résultats des évaluations
utils/
  auto_commit.py            # Helper pour commit automatique depuis Colab
```

## Utilisation (Google Colab)

Le workflow complet est dans [train_varroa.ipynb](train_varroa.ipynb). Il nécessite deux secrets Colab :

| Secret | Utilisation |
|--------|-------------|
| `GITHUB_TOKEN` | Clone et push vers ce dépôt |
| `ROBOFLOW_API_KEY` | Téléchargement du dataset |

Ordre d'exécution des cellules :
1. Installation des dépendances (`ultralytics`, `roboflow`)
2. Clone du dépôt et configuration Git
3. Téléchargement du dataset depuis Roboflow
4. Évaluation du modèle MDPI pré-entraîné
5. Fine-tuning avec le nouveau dataset
6. Évaluation du modèle fine-tuné
7. Inférence manuelle sur des images spécifiques
8. Commit des résultats vers GitHub

## Paramètres clés

| Paramètre | Valeur | Remarque |
|-----------|--------|----------|
| `imgsz` | 3900 (→ 3904) | Doit être multiple de 32 ; GPU 80 GB requis |
| `epochs` | 50 | |
| `batch` | 8 | |
| `conf` | 0.1 | Seuil bas pour maximiser le rappel |
| `max_det` | 2000 | Élevé car une image peut contenir des centaines de varroas |

## Résultats

| Dataset | Precision | Recall | mAP50 |
|---------|-----------|--------|-------|
| Train | 82.9 % | 79.9 % | 44.2 % |
| Val | 13.3 % | 24.9 % | 4.4 % |
| Test | 6.7 % | 12.5 % | 4.4 % |

L'écart train/test important indique un surapprentissage, principalement dû au faible nombre d'images de validation et de test.

## Limites et pistes d'amélioration

- Le modèle MDPI a été entraîné sur des planches sèches : il confond les gouttes d'eau et les débris de cire avec des varroas
- La détection de petits objets dans de très grandes images est coûteuse en mémoire (GPU 80 GB nécessaire pour 3900 px)
- Piste principale : utiliser **SAHI** (*Slicing Aided Hyper Inference*) pour découper les grandes images en tuiles avant l'inférence, ce qui permettrait de travailler avec des images standard sans GPU haut de gamme

## Référence

> Yániz, J.; Casalongue, M.; Martinez-de-Pison, F.J.; Silvestre, M.A.; Consortium, B.; Santolaria, P.; Divasón, J. *An AI-Based Open-Source Software for Varroa Mite Fall Analysis in Honeybee Colonies*. Agriculture 2025, 15, 969. https://doi.org/10.3390/agriculture15090969
