# Catex - Application de Prise de Rendez-vous

Application Streamlit pour gérer les rendez-vous entre clients et gérants.

## Installation

1. **Installer Python** (3.8+)
2. **Installer les dépendances:**
```bash
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur (http://localhost:8501)

## Fonctionnalités

### 👤 Clients
- Créer un compte
- Consulter les créneaux disponibles
- Réserver un rendez-vous
- Voir ses rendez-vous
- Annuler un rendez-vous
- Rechercher d'autres clients

### 🏢 Gérants
- Créer un compte (avec code d'accès)
- Consulter son agenda
- Ajouter/supprimer des créneaux disponibles
- Voir la liste complète des clients
- Annuler un rendez-vous

## Comptes de test

### Client
- Email: `client@test.fr`
- Mot de passe: `password123`

### Gérant
- Email: `gerant@test.fr`
- Mot de passe: `password123`
- Code d'accès: `CATEX2026GERANT`

## Stockage des données

Les données sont sauvegardées dans le fichier `catex_data.json` dans le répertoire courant.

## Notes

- Les données persistent entre les sessions
- Chaque rendezvous inclut des notifications automatiques
- L'application utilise `localStorage` du navigateur pour les données de session Streamlit
