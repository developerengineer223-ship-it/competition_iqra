// Minimal Express API for Allama Iqbal Platform
const express = require('express');
const app = express();

app.get('/api/verse-of-the-day', async (req, res) => {
  // TODO: Replace with DB fetch logic
  res.json({
    verse_id: 1,
    text_urdu: "خودی کو کر بلند اتنا",
    translations: [{ language: "en", text: "Raise thyself to such heights..." }],
    context: "From 'Bang-e-Dra', 1915",
    commentary: [{ author: "Scholar", text: "This verse emphasizes self-empowerment." }]
  });
});

module.exports = app;
