# Tp noté Kafka

## Participants :
- Defer Tanguy

## Porocédure pour déployer l'application dans un environnement de dev

* Pour lancer zookeeper, se mettre dans le dossier kafka et faire la commande:
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```
* Pour lancer kafka server, se mettre dans le dossier kafka et faire la commande:
```bash
bin/kafka-server-start.sh config/server.properties
```
* Pour lancer notre programme, ouvrir un terminal dans le projet et faire la commande:
```bash
python 3 /CHEMIN/DU/FICHIER/chat_client.py /join #general
```
* Pour lancer le producer kafka, se mettre dans le dossier kafka et faire la commande:
```bash
bin/kafka-console-producer.sh --topic chat_channel_general --bootstrap-server localhost:9092
```
