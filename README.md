# Concours — Adaptive Study

Code source de l'application d'étude adaptative mobile (PWA), version 3.20.0.

Le dépôt **public** contient le moteur et l'interface. Les PDF de cours, sujets et corrigés fournis par l'utilisateur, les images de leurs pages, ainsi que les données pédagogiques compilées ne sont pas publiés. Une copie fraîche du dépôt affiche les 7 matières et la structure des cours, sans banque de questions active.

## Restaurer l'application complète en local

Depuis l'archive privée `AdaptiveStudy_Originaux_623_2026-09-28.zip` conservée par le propriétaire :

```bash
python3 tools/restore_private_bundle.py /chemin/vers/AdaptiveStudy_Originaux_623_2026-09-28.zip
python3 -m http.server 8765 --directory local_instance/app
```

Ouvrir `http://127.0.0.1:8765/`. Sur Android avec Termux, exécuter `bash START_ADAPTIVE_STUDY.sh` après restauration. Les fichiers privés sont placés dans `local_instance/`, ignoré par Git.

Le paquet privé donne accès à 623 unités originales sous forme de pages de sujet et de corrigé (549 QCM et 74 QROC). Ces unités ne sont pas transcrites et notées automatiquement. Les anciens QCM et flashcards générés sont désactivés. Les dossiers d'exercices de physique et de biochimie demandent encore une intégration complète avec leurs documents et corrigés.

## Structure

- `app/app.js` : navigation, sessions et lecteur de documents originaux.
- `app/styles.css`, `app/index.html`, `app/manifest.webmanifest`, `app/sw.js` : interface et installation PWA.
- `app/content.js`, `app/original_corpus.js`, `app/exercises.js` : **squelettes publics** remplacés localement par les versions privées de l'archive.
- `tools/restore_private_bundle.py` : restauration locale des données depuis l'archive privée, sans réseau.

## Sources et traçabilité

Toute future question ou flashcard doit être justifiée par les PDF de cours, QE, annales et corrigés fournis. Les flashcards proviennent des cours ; les annales/QE servent à comprendre le style. Ne jamais conclure qu'une proposition est fausse parce qu'elle n'est pas mentionnée dans un PDF. Les documents incomplets et les questions dérivées non vérifiées restent désactivés.
