const express = require('express'),
  router = express.Router(),
  fs = require('fs'),
  path = require('path'),
  utils = require('../utils/utils'),
  Products = require('../models/Products.js')

router.get('/api/products', async function (req, res) {

  let query = {}
  let page = req.query.page && typeof parseInt(req.query.page) === 'number' ? req.query.page : 1
  let pageSize = 40

  if (req.query.search) {
    let splitSearch = req.query.search.toLowerCase().split(' ')
    let regex = ''
    splitSearch.forEach(word => {
      regex += '(?=.*' + word + ')'
    })
    regex += '.*'
    query.name = {$regex: regex, $options: 'i'}
  }

  let price = {}
  if (req.query.minPrice && parseInt(req.query.minPrice) !== -1) {
    price.$gt = parseInt(req.query.minPrice)
  }
  if (req.query.maxPrice && parseInt(req.query.maxPrice) !== -1) {
    price.$lt = parseInt(req.query.maxPrice)
  }
  if (Object.keys(price).length > 0) {
    query.price = price
  }

  let minMaxPrice = await Products.aggregate([
    {$match: query},
    {
      '$group': {
        '_id': null,
        'max': {'$max': '$price'},
        'min': {'$min': '$price'}
      }
    }
  ])

  let min = parseInt(req.query.minPrice) !== -1 ? parseInt(req.query.minPrice) : minMaxPrice.length > 0 ? Math.floor(minMaxPrice[0].min) : -1
  let max = parseInt(req.query.maxPrice) !== -1 ? parseInt(req.query.maxPrice) : minMaxPrice.length > 0 ? Math.ceil(minMaxPrice[0].max) : -1

  let products = await Products.find(query).skip(pageSize * (page - 1)).limit(pageSize)
  let nbPage = Math.ceil(await Products.find(query).count() / pageSize)

  await utils.asyncForEach(products, async (product, i) => {
    if (!fs.existsSync(path.join(__dirname, '..', '..', 'scrapies', 'data', product.store, 'img', product.image_name + '.jpg'))) {
      products[i].image_name = 'default'
    }

    let minPrice = -1
    let maxPrice = -1

    let similarProducts = await Products.find({'_id': {$in: product.similarities}})

    await utils.asyncForEach(similarProducts, async (similarProduct) => {
      if (similarProduct.price < minPrice || minPrice === -1) {
        minPrice = similarProduct.price
      }
      if (similarProduct.price > maxPrice || maxPrice === -1) {
        maxPrice = similarProduct.price
      }
    })

    product.minPrice = minPrice
    product.maxPrice = maxPrice
  })

  res.json({products, nbPage, min, max})
})

router.get('/api/product/:id', async function (req, res) {
  let product = await Products.findOne({'_id': req.params.id})
  if (!fs.existsSync(path.join(__dirname, '..', '..', 'scrapies', 'data', product.store, 'img', product.image_name + '.jpg'))) {
    product.image_name = 'default'
  }
  let similarProducts = await Products.find({'_id': {$in: product.similarities}})
  res.json({product, similarProducts})
})

module.exports = router
