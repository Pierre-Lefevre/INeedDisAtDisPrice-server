const fs = require('fs'),
  path = require('path')

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
