# INeedDisAtDisPrice-server

## Raspberry Pi

### Crontab

Modifier la crontab :

```bash
$ crontab -e
```

Le script bash cron.sh sera exécuté tous les jours à minuit :

```bash
m h  dom mon dow   command
0 0 * * * bash ~/INeedDisAtDisPrice-server/cron.sh
```

### Mongo

Lancer le serveur Mongo :

```bash
$ sudo mongod
```

### API

Lancer l'API :

```bash
$ cd ~/INeedDisAtDisPrice-server/server
$ npm install
$ npm run start
```
