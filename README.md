# INeedDisAtDisPrice-server

## Raspberry

### Crontab

Modifier la crontab :

```bash
$ crontab -e
```

Le script bash cron.sh sera exécuté toutes les minutes :

```bash
m h  dom mon dow   command
* * * * * bash ~/INeedDisAtDisPrice-server/cron.sh
```

### Mongo

Lancer le serveur Mongo :

```bash
$ sudo mongod
```

### I Need Dis At Dis Price - serveur

Lancer le serveur de l'application :

```bash
$ cd ~/INeedDisAtDisPrice/server
$ npm run start
```

Tuer un processus qui écoute un port :

```bash
$ sudo netstat -tulpn | grep LISTEN
$ kill -9 PROCESS_ID
```
