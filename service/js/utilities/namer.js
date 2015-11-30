(function() {
  var Namer;

  Namer = (function() {
    function Namer() {}

    Namer.prototype.generate = function() {
      var adjs, nouns, numAdj, numNouns, rnd;
      adjs = ["autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark", "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter", "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue", "billowing", "broken", "cold", "damp", "falling", "frosty", "green", "long", "late", "lingering", "bold", "little", "morning", "muddy", "old", "red", "rough", "still", "small", "sparkling", "throbbing", "shy", "aged", "wandering", "withered", "wild", "black", "young", "holy", "solitary", "fragrant", "snowy", "proud", "floral", "restless", "divine", "polished", "ancient", "purple", "lively", "nameless"];
      nouns = ["waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning", "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter", "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook", "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly", "feather", "grass", "haze", "mountain", "night", "pond", "darkness", "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder", "violet", "water", "wildflower", "wave", "water", "resonance", "sun", "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper", "frog", "smoke", "star"];
      numAdj = adjs.length;
      numNouns = nouns.length;
      rnd = Math.floor(Math.random() * Math.pow(2, 12));
      return adjs[rnd >> 6 % numAdj] + "-" + nouns[rnd % numNouns];
    };

    return Namer;

  })();

  if (this.namer == null) {
    this.namer = new Namer;
  }

}).call(this);
