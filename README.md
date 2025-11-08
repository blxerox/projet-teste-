# Assistant d'anniversaires clients

Cette application Python propose une interface graphique claire et moderne pour
vous aider à souhaiter un joyeux anniversaire à vos clients et à leur envoyer
rapidement un message personnalisé.

## Fonctionnalités

- Affichage de la liste des clients avec leur email, leur âge et la date de
  leur prochain anniversaire.
- Alerte automatique lorsque des clients fêtent leur anniversaire aujourd'hui.
- Message d'anniversaire prérempli personnalisable, incluant le prénom du
  destinataire.
- Envoi (simulation) du message aux clients sélectionnés ou à tous les clients
  dont c'est l'anniversaire du jour.
- Historique des messages envoyés pour garder une trace de vos actions.

## Prérequis

- Python 3.10 ou plus récent

Toutes les bibliothèques utilisées font partie de la bibliothèque standard de
Python (Tkinter). Aucun paquet supplémentaire n'est nécessaire.

## Installation

1. Clonez le dépôt ou copiez les fichiers sur votre machine.
2. Facultatif : modifiez `data/clients.json` pour y ajouter vos propres clients.
   Chaque entrée doit respecter le format suivant :

   ```json
   {
     "name": "Prénom Nom",
     "email": "adresse@example.com",
     "birthday": "AAAA-MM-JJ"
   }
   ```

## Exécution

Lancez l'interface graphique avec la commande :

```bash
python birthday_notifier.py
```

La fenêtre affiche automatiquement les anniversaires du jour et vous permet de
sélectionner un ou plusieurs clients pour leur envoyer un message personnalisé.

## Personnalisation du message

- Le champ de message contient un modèle par défaut que vous pouvez modifier.
- Assurez-vous de conserver le placeholder `{name}` pour insérer le nom du
  client automatiquement lors de l'envoi.

## Notes

- L'envoi de messages est simulé : les messages ne sont pas réellement expédiés
  mais enregistrés dans l'historique, prêt à être copié/collé dans votre outil
  de communication.
- Ajoutez autant de clients que nécessaire dans `data/clients.json` pour adapter
  l'application à vos besoins.
