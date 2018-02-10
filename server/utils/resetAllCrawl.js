const fs = require('fs'),
  path = require('path'),
  mongoose = require('mongoose'),
  config = require('../config/config'),
  Alerts = require('../models/Alerts.js'),
  Products = require('../models/Products.js')

resetAllCrawl()

async function resetAllCrawl () {

  await mongoose.connect(config.mongoUrl)
  await Alerts.collection.remove()
  await Products.collection.remove()

  let stores = ['auchan', 'boulanger', 'cdiscount', 'darty', 'fnac', 'ldlc', 'materiel_net', 'rue_du_commerce']
  let jsonFolders = []

  stores.forEach(store => {
    jsonFolders.push(path.join(__dirname, '..', '..', 'scrapies', 'data', store, 'img'))
    jsonFolders.push(path.join(__dirname, '..', '..', 'scrapies', 'data', store, 'json'))
  })

  jsonFolders.forEach(jsonFolder => {
    fs.readdirSync(jsonFolder).forEach(file => {
      if (file !== '.gitignore') {
        fs.unlinkSync(path.join(jsonFolder, file))
      }
    })
  })

  fs.writeFileSync(path.join(__dirname, '..', '..', 'scrapies', 'already_crawled.json'), JSON.stringify([]), 'utf8')

  process.exit()
}
