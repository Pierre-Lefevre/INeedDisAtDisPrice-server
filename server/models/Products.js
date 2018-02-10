const mongoose = require('mongoose')

let Schema = mongoose.Schema

const productsSchema = new Schema({
  store: String,
  url: String,
  main_category: String,
  categories: Array,
  brand: String,
  openssl_hash: String,
  name: String,
  price_old: Number,
  price: Number,
  currency: String,
  image_urls: Array,
  image_name: String,
  rate: Number,
  max_rate: Number,
  nb_avis: Number,
  price_history: Array,
  similarities: Array,
  maxPrice: Number,
  minPrice: Number
}, {
  strict: false,
  versionKey: false
})

const Products = mongoose.model('products', productsSchema)

module.exports = Products
