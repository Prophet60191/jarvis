const express = require('express');
const router = express.Router();
const Button = require('../models/Button');

router.get('/color', async (req, res) => {
  try {
    const button = await Button.findOne({ userId: req.user.userId });
    if (!button) return res.status(404).send({ message: 'Button not found' });
    // Return the current color of the button
    res.send(button.color);
  } catch (error) {
    console.error(error);
    res.status(500).send({ message: 'Error fetching button color' });
  }
});

router.put('/color', async (req, res) => {
  try {
    const button = await Button.findOneAndUpdate({ userId: req.user.userId }, { color: req.body.color }, { new: true });
    if (!button) return res.status(404).send({ message: 'Button not found' });
    // Update the button color
    res.send(button);
  } catch (error) {
    console.error(error);
    res.status(500).send({ message: 'Error updating button color' });
  }
});

module.exports = router;
