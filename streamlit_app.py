import streamlit as st
import requests
from backend import app
from models import db, Summary
from utils import extract_text_from_pdf, extract_text_from_docx, extract_grammatical_info, save_summary_as_pdf, save_summary_as_word
import pandas as pd

def delete_summary(summary_id):
    response = requests.delete(f'http://localhost:5000/delete_summary/{summary_id}')
    return response.json()

def main():
    st.sidebar.title("Options")
    language = st.sidebar.selectbox("Sélectionnez la langue", ["en", "fr"])
    precision = st.sidebar.slider("Niveau de précision", 0.1, 1.0, 0.5)
    
    st.sidebar.title("Historique des résumés")
    with app.app_context():
        summaries = Summary.query.all()
        
        # Afficher les résumés avec boutons de visualisation et de suppression
        for summary in summaries:
            col1, col2 = st.sidebar.columns([3, 1])
            
            # Bouton pour afficher le résumé
            with col1:
                if st.button(f"Résumé {summary.id}", key=f"view_{summary.id}"):
                    st.sidebar.text_area("Contenu du résumé", 
                                       value=summary.summary,
                                       height=150,
                                       key=f"text_{summary.id}")
            
            # Bouton pour supprimer le résumé
            with col2:
                if st.button("🗑️", key=f"delete_{summary.id}"):
                    result = delete_summary(summary.id)
                    if result.get("success"):
                        st.sidebar.success("Résumé supprimé avec succès")
                        st.rerun()  # Recharger la page
                    else:
                        st.sidebar.error(f"Erreur: {result.get('message')}")
        
        # Bouton pour tout effacer
        if summaries:  # N'afficher le bouton que s'il y a des résumés
            if st.sidebar.button("Effacer tous les résumés"):
                try:
                    with app.app_context():
                        for summary in summaries:
                            delete_summary(summary.id)
                    st.sidebar.success("Tous les résumés ont été supprimés")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Erreur lors de la suppression : {str(e)}")
    
    st.title("Générateur de Résumés")
    text = st.text_area("Entrez le texte à résumer")
    uploaded_file = st.file_uploader("Ou téléchargez un fichier", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
    
    if st.button("Générer le résumé"):
        if text:
            response = requests.post('http://localhost:5000/summarize', 
                                   json={'text': text, 'language': language, 'precision': precision})
            summary = response.json()['summary']
            
            # Afficher le résumé
            st.write("Résumé généré:")
            st.write(summary)
            
            # Afficher les informations grammaticales
            grammatical_info = extract_grammatical_info(summary, language)
            df = pd.DataFrame(grammatical_info, columns=["Sujet", "Verbe", "Complément"])
            st.write("Informations grammaticales extraites:")
            st.table(df)
            
            try:
                # Générer les fichiers
                pdf_data = save_summary_as_pdf(summary)
                word_data = save_summary_as_word(summary)
                
                # Boutons de téléchargement
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Télécharger le PDF",
                        data=pdf_data,
                        file_name="résumé.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    st.download_button(
                        label="Télécharger le Word",
                        data=word_data,
                        file_name="résumé.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"Erreur lors de la génération des fichiers : {str(e)}")
        else:
            st.write("Veuillez entrer du texte ou télécharger un fichier.")

if __name__ == '__main__':
    main()