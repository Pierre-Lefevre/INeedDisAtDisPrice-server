const mongoose = require('mongoose'),
  nodemailer = require('nodemailer'),
  config = require('../config/config'),
  utils = require('./utils'),
  Alerts = require('../models/Alerts.js'),
  Products = require('../models/Products.js'),
  Users = require('../models/Users.js')

mongoose.connect(config.mongoUrl)

let transporter = nodemailer.createTransport({
  pool: true,
  host: 'smtp.gmail.com',
  port: 465,
  secure: true,
  auth: {
    user: 'lefevre.pierre.m.d@gmail.com',
    pass: 'cilalvetraee'
  }
})

checkAlerts()

async function checkAlerts () {
  let alerts = await Alerts.find()

  await utils.asyncForEach(alerts, async (alert) => {
    let product = await Products.findOne({_id: alert.id_product})


    product.price = 0
    if (!alert.done && product.price <= alert.price) {
      let user = await Users.findOne({_id: alert.id_user})
      await sendEmail({
        from: 'lefevre.pierre.m.d@gmail.com',
        to: user.email,
        subject: 'I Need Dis At Dis Price - Alerte prix',
        html: '<p style="margin-bottom: 30px">Bonjour <b>' + user.firstname + ' ' + user.lastname + '</b>,</p>' +
        '<p>Vous souhaitiez être averti lorsque le produit intitulé "' + product.name + '" sera disponible pour moins de ' + alert.price + ' ' + utils.currencySymbol(product.currency) + '.</p>' +
        '<p>C\'est désormais chose faite, vous le trouverez à ' + product.price + ' ' + utils.currencySymbol(product.currency) + ' en cliquant sur le lien suivant :</p>' +
        '<a href="http://localhost:8080/#/product/' + product._id + '" target="_blank">' + product.name + '</a>' +
        '<p style="margin-top: 30px">Cordialement,</p>' +
        '<p>L\'équipe <b>I Need Dis At Dis Price</b>.</p>'
      })
      // alert.done = true
      // await alert.save()
    }
  })

  process.exit()
}

async function sendEmail (mailOptions) {
  await transporter.sendMail(mailOptions).then(function (info) {
    console.log('Message sent: ' + info.messageId)
  }).catch(function (err) {
    console.log(err)
  })
}
