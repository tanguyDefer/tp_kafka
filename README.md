# Tp noté Kafka

## Participants :
- Defer Tanguy
- Nohet Floriane
- Sayez Jacques

## Porocédure pour déployer l'application dans un environnement de dev

* Pour lancer zookeeper, se mettre dans le dossier kafka et faire la commande:
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```
* Pour lancer kafka server, se mettre dans le dossier kafka et faire la commande:
```bash
bin/kafka-server-start.sh config/server.properties
```
* Pour ouvrir un consumer kafka, se mettre dans le dossier kafka et faire la commande:
```bash
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic chat_chanel_consumer
```
* Pour lancer notre programme, ouvrir un terminal dans le projet et faire la commande:
```bash
python 3 /CHEMIN/DU/FICHIER/chat_client.py USER
```
* Dans notre programme pour rejoindre un channel:
```bash
/join #CHANNEL_NAME
```
* Dans notre programme pour quitter un channel:
```bash
/part #CHANNEL_NAME
```
* Dans notre programme pour quitter le programme:
```bash
/quit #CHANNEL_NAME
```
* Pour lancer le producer kafka, se mettre dans le dossier kafka et faire la commande:
```bash
bin/kafka-console-producer.sh --topic chat_channel_general --bootstrap-server localhost:9092
```
* Pour lancer le programme bit_channel.py, ouvrir un nouveau terminal, se mettre dans le dossier spark et faire la commande:
```bash
bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 /folder/to/file/location/bot_channel.py
```
