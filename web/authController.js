const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const User = require('../models/User');

router.post('/register', async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const user = new User({ username: req.body.username, password: hashedPassword });
    await user.save();
    res.status(201).send({ message: 'User created successfully' });
  } catch (error) {
    console.error(error);
    res.status(500).send({ message: 'Error creating user' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const user = await User.findOne({ username: req.body.username });
    if (!user) return res.status(401).send({ message: 'Invalid credentials' });
    const isValidPassword = await bcrypt.compare(req.body.password, user.password);
    if (!isValidPassword) return res.status(401).send({ message: 'Invalid credentials' });
    // Generate JWT token
    const token = jwt.sign({ userId: user._id }, process.env.SECRET_KEY, { expiresIn: '1h' });
    res.send({ token });
  } catch (error) {
    console.error(error);
    res.status(500).send({ message: 'Error logging in' });
  }
});

module.exports = router;
