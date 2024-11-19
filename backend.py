from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Summary
from utils import generate_summary

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summaries.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data['text']
    language = data['language']
    precision = data['precision']
    summary = generate_summary(text, language, precision)
    new_summary = Summary(text=text, summary=summary, language=language)
    db.session.add(new_summary)
    db.session.commit()
    return jsonify({'summary': summary})

@app.route('/delete_summary/<int:summary_id>', methods=['DELETE'])
def delete_summary(summary_id):
    try:
        summary = Summary.query.get(summary_id)
        if summary:
            db.session.delete(summary)
            db.session.commit()
            return jsonify({"success": True, "message": "Résumé supprimé avec succès"})
        return jsonify({"success": False, "message": "Résumé non trouvé"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500