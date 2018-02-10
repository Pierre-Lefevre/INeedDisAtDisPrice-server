const fs = require('fs'),
  path = require('path'),
  mongoose = require('mongoose'),
  config = require('../config/config'),
  utils = require('./utils'),
  Products = require('../models/Products.js')

loadJsonInDb()

async function loadJsonInDb () {

  await mongoose.connect(config.mongoUrl)

  await Products.collection.remove()

  let stores = ['auchan', 'boulanger', 'cdiscount', 'darty', 'fnac', 'ldlc', 'materiel_net', 'rue_du_commerce']
  let jsonFolders = []
  let newIds = []
  let documents = []
  let frequentWords = []

  stores.forEach(store => {
    jsonFolders.push(path.join(__dirname, '..', '..', 'scrapies', 'data', store, 'json'))
  })

  jsonFolders.forEach(jsonFolder => {
    fs.readdirSync(jsonFolder).forEach(file => {
      if (file.endsWith('.json')) {
        try {
          documents.push(JSON.parse(fs.readFileSync(path.join(jsonFolder, file), 'utf8')))
        } catch (e) {
          console.log(e.message)
        }
      }
    })
  })

  //Récupère les produits insérés.
  let newProducts = await Products.create(documents)

  // Récupère tous les produits.
  let allProducts = await Products.find()

  // let allWordsWithFrequence = await Products.aggregate([
  //   {
  //     $project: {
  //       words: {$split: [{$toLower: '$name'}, ' ']}
  //     }
  //   },
  //   {
  //     $unwind: {
  //       path: '$words'
  //     }
  //   },
  //   {
  //     $group: {
  //       _id: '$words',
  //       count: {$sum: 1}
  //     }
  //   },
  //   {
  //     $sort: {count: -1}
  //   }
  // ])

  let allWordsWithFrequenceObject = {}
  await utils.asyncForEach(allProducts, async (product) => {
    let splitName = product.name.split(' ')
    splitName.forEach(word => {
      if (allWordsWithFrequenceObject.hasOwnProperty(word.toLowerCase())) {
        allWordsWithFrequenceObject[word.toLowerCase()]++
      } else {
        allWordsWithFrequenceObject[word.toLowerCase()] = 1
      }
    })
  })

  let allWordsWithFrequence = []
  Object.keys(allWordsWithFrequenceObject).filter((key, i) => {
    allWordsWithFrequence.push({word: key, count: allWordsWithFrequenceObject[key]})
  })
  allWordsWithFrequence.sort((a, b) => {return a.count < b.count ? 1 : -1})

  allWordsWithFrequence.every(word => {

    // Récupère les mots présents dans plus de 10% des produits.
    if (word.count >= allProducts.length * 0.1) {
      frequentWords.push(word._id)
      return true
    }
    return false
  })

  newProducts.forEach(product => {
    newIds.push(product._id.toString())
  })

  await utils.asyncForEach(newProducts, async (product1) => {
    product1.similarities = []
    await utils.asyncForEach(allProducts, async (product2) => {
      if (!product1._id.equals(product2._id) && (editDistancePercentSimilarity(product1.name, product2.name) > 0.9 || wordPercentSimilarity(frequentWords, product1.name, product2.name) > 0.8)) {
        product1.similarities.push(product2._id.toString())
        if (newIds.indexOf(product2._id.toString()) === -1 && product2.similarities.indexOf(product1._id.toString()) === -1) {
          product2.similarities.push(product1._id.toString())
          await product2.save()
        }
      }
    })
    await product1.save()
  })

  let idMapping = {}
  let allIdsToGet = []

  newProducts.forEach(product => {
    if (product.similarities.length > 0) {
      for (let i = 0; i < product.similarities.length; i++) {
        allIdsToGet.push(product.similarities[i])
        if (idMapping.hasOwnProperty(product.similarities[i])) {
          idMapping[product.similarities[i]].push(product._id)
        } else {
          idMapping[product.similarities[i]] = [product._id]
        }
      }
    }
  })

  // jsonFolders.forEach(jsonFolder => {
  //   fs.readdirSync(jsonFolder).forEach(file => {
  //     if (file.endsWith('.json')) {
  //       fs.unlinkSync(path.join(jsonFolder, file))
  //     }
  //   })
  // })

  process.exit()
}

function wordPercentSimilarity (frequentWords, s1, s2) {
  let s1Split = s1.split(' ')
  let s2Split = s2.split(' ')

  utils.lowerCaseArray(s1Split)
  utils.lowerCaseArray(s2Split)

  s1Split.forEach((word, i) => {
    if (word === '+' || word === '-') {
      s1Split.splice(i, 1)
      return
    }
    if (word.startsWith('-')) {
      word = word.substr(1)
      s1Split[i] = word
    }
    if (word.endsWith('-')) {
      word = word.substring(0, word.length - 1)
      s1Split[i] = word
    }
  })

  Array.prototype.diff = function (a) {
    return this.filter(function (i) {return a.indexOf(i) < 0})
  }

  s1Split = s1Split.diff(frequentWords)
  s2Split = s2Split.diff(frequentWords)

  return (s1Split.length - s1Split.diff(s2Split).length) * 2 / (s1Split.length + s2Split.length)

  // let percent = (s1Split.length - s1Split.diff(s2Split).length) * 2 / (s1Split.length + s2Split.length)
  // if (percent > 0.8) {
  //   console.log(s1Split)
  //   console.log(s2Split)
  //   console.log('--------')
  // }
  // return percent
}

function editDistancePercentSimilarity (s1, s2) {
  s1 = s1.toLowerCase()
  s2 = s2.toLowerCase()

  let longer = s1
  let shorter = s2

  if (s1.length < s2.length) {
    longer = s2
    shorter = s1
  }
  let longerLength = longer.length
  if (longerLength === 0) {
    return 1.0
  }
  return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength)
}

function editDistance (a, b) {
  if (a.length === 0) return b.length
  if (b.length === 0) return a.length

  let matrix = []

  // increment along the first column of each row
  let i
  for (i = 0; i <= b.length; i++) {
    matrix[i] = [i]
  }

  // increment each column in the first row
  let j
  for (j = 0; j <= a.length; j++) {
    matrix[0][j] = j
  }

  // Fill in the rest of the matrix
  for (i = 1; i <= b.length; i++) {
    for (j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(matrix[i - 1][j - 1] + 1, Math.min(matrix[i][j - 1] + 1, matrix[i - 1][j] + 1))
      }
    }
  }

  return matrix[b.length][a.length]
}
