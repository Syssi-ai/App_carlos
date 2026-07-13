import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Configuration de la page
st.set_page_config(page_title="Catex - Prise de rendez-vous", layout="wide")

# Initialisation du session state
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "view" not in st.session_state:
    st.session_state.view = "auth"
if "users" not in st.session_state:
    st.session_state.users = []
if "slots" not in st.session_state:
    st.session_state.slots = []
if "notifs" not in st.session_state:
    st.session_state.notifs = []

# Constantes
GERANT_CODE = "CATEX2026GERANT"
STORAGE_FILE = "catex_data.json"

# ========== FONCTIONS DE STOCKAGE ==========
def load_all_data():
    """Charger les données depuis le fichier JSON"""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.users = data.get("users", [])
            st.session_state.slots = data.get("slots", [])
            st.session_state.notifs = data.get("notifs", {})
    else:
        st.session_state.users = []
        st.session_state.slots = []
        st.session_state.notifs = {}

def save_all_data():
    """Sauvegarder les données dans le fichier JSON"""
    data = {
        "users": st.session_state.users,
        "slots": st.session_state.slots,
        "notifs": st.session_state.notifs
    }
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_user(email):
    """Trouver un utilisateur par email"""
    for u in st.session_state.users:
        if u["email"].lower() == email.lower():
            return u
    return None

def add_notif(email, message):
    """Ajouter une notification"""
    if email not in st.session_state.notifs:
        st.session_state.notifs[email] = []
    st.session_state.notifs[email].insert(0, {
        "id": f"n{int(datetime.now().timestamp())}",
        "message": message,
        "date": datetime.now().isoformat(),
        "lu": False
    })
    save_all_data()

# ========== PAGE AUTHENTIFICATION ==========
def render_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔘 Catex")
        st.markdown("Prenez rendez-vous en quelques clics")
        
        tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
        
        with tab1:
            st.subheader("Connexion")
            email = st.text_input("Adresse e-mail", key="login_email")
            password = st.text_input("Mot de passe", type="password", key="login_password")
            
            if st.button("Se connecter", use_container_width=True):
                user = find_user(email)
                if user and user["password"] == password:
                    st.session_state.current_user = user
                    st.session_state.view = "manager" if user["role"] == "gerant" else "client"
                    st.success("Connexion réussie!")
                    st.rerun()
                else:
                    st.error("E-mail ou mot de passe incorrect.")
        
        with tab2:
            st.subheader("Créer un compte")
            role = st.radio("Rôle", ["client", "gerant"], horizontal=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                prenom = st.text_input("Prénom")
            with col_b:
                nom = st.text_input("Nom")
            
            email_reg = st.text_input("Adresse e-mail", key="reg_email")
            tel = st.text_input("Téléphone", placeholder="06 12 34 56 78")
            adresse = st.text_input("Adresse postale", placeholder="12 rue des Lilas, Nantes")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password_reg = st.text_input("Mot de passe", type="password", key="reg_password")
            with col_p2:
                password_conf = st.text_input("Confirmer", type="password", key="reg_password_conf")
            
            if role == "gerant":
                code = st.text_input("Code d'accès gérant")
            else:
                code = None
            
            if st.button("Créer mon compte", use_container_width=True):
                if password_reg != password_conf:
                    st.error("Les mots de passe ne correspondent pas.")
                elif role == "gerant" and code != GERANT_CODE:
                    st.error("Code d'accès gérant invalide.")
                elif find_user(email_reg):
                    st.error("Un compte existe déjà avec cet e-mail.")
                elif not all([prenom, nom, email_reg, tel, adresse, password_reg]):
                    st.error("Tous les champs sont obligatoires.")
                else:
                    new_user = {
                        "email": email_reg.lower(),
                        "password": password_reg,
                        "prenom": prenom,
                        "nom": nom,
                        "telephone": tel,
                        "adresse": adresse,
                        "role": role
                    }
                    st.session_state.users.append(new_user)
                    st.session_state.current_user = new_user
                    st.session_state.view = "manager" if role == "gerant" else "client"
                    save_all_data()
                    st.success("Compte créé avec succès!")
                    st.rerun()

# ========== PAGE CLIENT ==========
def render_client():
    st.sidebar.markdown(f"### {st.session_state.current_user['prenom']} {st.session_state.current_user['nom']}")
    st.sidebar.markdown("**Client**")
    
    page = st.sidebar.radio("Menu", ["Prendre RDV", "Mes RDV", "Rechercher"])
    
    if st.sidebar.button("Déconnexion"):
        st.session_state.current_user = None
        st.session_state.view = "auth"
        st.rerun()
    
    st.title("Catex - Prise de rendez-vous")
    
    if page == "Prendre RDV":
        st.subheader("Prendre rendez-vous")
        libres = [s for s in st.session_state.slots if s["statut"] == "libre"]
        
        if not libres:
            st.info("Aucun créneau disponible pour le moment.")
        else:
            libres_sorted = sorted(libres, key=lambda x: x["date"] + x["heure"])
            for slot in libres_sorted:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📅 {slot['date']} à {slot['heure']}")
                with col2:
                    if st.button("Réserver", key=f"book_{slot['id']}"):
                        slot["statut"] = "reserve"
                        slot["clientEmail"] = st.session_state.current_user["email"]
                        save_all_data()
                        
                        # Notifier les gérants
                        for user in st.session_state.users:
                            if user["role"] == "gerant":
                                add_notif(user["email"], 
                                    f"{st.session_state.current_user['prenom']} {st.session_state.current_user['nom']} a pris rendez-vous le {slot['date']} à {slot['heure']}.")
                        
                        add_notif(st.session_state.current_user["email"], 
                            f"Votre rendez-vous du {slot['date']} à {slot['heure']} est confirmé.")
                        
                        st.success("Rendez-vous confirmé!")
                        st.rerun()
    
    elif page == "Mes RDV":
        st.subheader("Mes rendez-vous")
        mine = [s for s in st.session_state.slots 
                if s.get("clientEmail") == st.session_state.current_user["email"]]
        
        if not mine:
            st.info("Vous n'avez aucun rendez-vous.")
        else:
            mine_sorted = sorted(mine, key=lambda x: x["date"] + x["heure"])
            for slot in mine_sorted:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    status_badge = "✅ Confirmé" if slot["statut"] == "reserve" else f"❌ {slot['statut']}"
                    st.write(f"📅 {slot['date']} à {slot['heure']} - {status_badge}")
                with col3:
                    if slot["statut"] == "reserve" and st.button("Annuler", key=f"cancel_{slot['id']}"):
                        slot["statut"] = "libre"
                        slot["clientEmail"] = None
                        save_all_data()
                        
                        for user in st.session_state.users:
                            if user["role"] == "gerant":
                                add_notif(user["email"], 
                                    f"{st.session_state.current_user['prenom']} {st.session_state.current_user['nom']} a annulé son RDV du {slot['date']} à {slot['heure']}.")
                        
                        add_notif(st.session_state.current_user["email"], 
                            f"Vous avez annulé votre RDV du {slot['date']} à {slot['heure']}.")
                        
                        st.success("Rendez-vous annulé.")
                        st.rerun()
    
    elif page == "Rechercher":
        st.subheader("Rechercher un client")
        search_query = st.text_input("Rechercher par nom ou prénom...")
        
        if search_query:
            results = [u for u in st.session_state.users 
                      if u["role"] == "client" 
                      and u["email"] != st.session_state.current_user["email"]
                      and (search_query.lower() in u["nom"].lower() or search_query.lower() in u["prenom"].lower())]
            
            if results:
                for u in results:
                    st.write(f"👤 {u['prenom']} {u['nom']} - {u['email']} - {u['telephone']}")
            else:
                st.info("Aucun client trouvé.")

# ========== PAGE GÉRANT ==========
def render_manager():
    st.sidebar.markdown(f"### {st.session_state.current_user['prenom']} {st.session_state.current_user['nom']}")
    st.sidebar.markdown("**Gérant**")
    
    page = st.sidebar.radio("Menu", ["Agenda", "Disponibilités", "Mes clients"])
    
    if st.sidebar.button("Déconnexion"):
        st.session_state.current_user = None
        st.session_state.view = "auth"
        st.rerun()
    
    st.title("Catex - Espace Gérant")
    
    if page == "Agenda":
        st.subheader("Agenda")
        rdv = [s for s in st.session_state.slots if s["statut"] == "reserve"]
        
        if not rdv:
            st.info("Aucun rendez-vous programmé.")
        else:
            rdv_sorted = sorted(rdv, key=lambda x: x["date"] + x["heure"])
            for slot in rdv_sorted:
                client = find_user(slot.get("clientEmail", ""))
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"📅 {slot['date']} à {slot['heure']}")
                with col2:
                    if client:
                        st.write(f"👤 {client['prenom']} {client['nom']} - {client['telephone']}")
                with col3:
                    if st.button("Annuler", key=f"cancel_mgr_{slot['id']}"):
                        slot["statut"] = "libre"
                        client_email = slot.get("clientEmail")
                        slot["clientEmail"] = None
                        save_all_data()
                        
                        if client:
                            add_notif(client_email, 
                                f"Votre gérant a annulé votre RDV du {slot['date']} à {slot['heure']}.")
                        
                        st.success("Rendez-vous annulé.")
                        st.rerun()
    
    elif page == "Disponibilités":
        st.subheader("Mes disponibilités")
        
        col1, col2 = st.columns(2)
        with col1:
            slot_date = st.date_input("Date")
        with col2:
            slot_time = st.time_input("Heure")
        
        if st.button("Ajouter le créneau", use_container_width=True):
            date_str = slot_date.strftime("%Y-%m-%d")
            time_str = slot_time.strftime("%H:%M")
            
            exists = any(s["date"] == date_str and s["heure"] == time_str for s in st.session_state.slots)
            if exists:
                st.error("Ce créneau existe déjà.")
            else:
                st.session_state.slots.append({
                    "id": f"s{int(datetime.now().timestamp())}",
                    "date": date_str,
                    "heure": time_str,
                    "statut": "libre",
                    "clientEmail": None
                })
                save_all_data()
                st.success("Créneau ajouté.")
                st.rerun()
        
        st.markdown("---")
        st.write("**Créneaux disponibles:**")
        
        libres = [s for s in st.session_state.slots if s["statut"] == "libre"]
        if not libres:
            st.info("Aucun créneau disponible.")
        else:
            libres_sorted = sorted(libres, key=lambda x: x["date"] + x["heure"])
            for slot in libres_sorted:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📅 {slot['date']} à {slot['heure']}")
                with col2:
                    if st.button("Supprimer", key=f"delete_{slot['id']}"):
                        st.session_state.slots = [s for s in st.session_state.slots if s["id"] != slot["id"]]
                        save_all_data()
                        st.success("Créneau supprimé.")
                        st.rerun()
    
    elif page == "Mes clients":
        st.subheader("Mes clients")
        clients = [u for u in st.session_state.users if u["role"] == "client"]
        
        if not clients:
            st.info("Aucun client inscrit.")
        else:
            search = st.text_input("Rechercher un client...")
            filtered = [c for c in clients 
                       if not search or search.lower() in c["nom"].lower() 
                       or search.lower() in c["prenom"].lower()
                       or search.lower() in c["email"].lower()]
            
            df = pd.DataFrame(filtered, columns=["nom", "prenom", "email", "telephone", "adresse"])
            st.dataframe(df, use_container_width=True)

# ========== MAIN ==========
def main():
    load_all_data()
    
    if st.session_state.view == "auth":
        render_auth()
    elif st.session_state.view == "client":
        render_client()
    elif st.session_state.view == "manager":
        render_manager()

if __name__ == "__main__":
    main()
