const express = require('express');
const router = express.Router();
const authController = require('./controllers/authController');
const buttonController = require('./controllers/buttonController');

router.use('/auth', authController);
router.use('/button', buttonController);

module.exports = router;
