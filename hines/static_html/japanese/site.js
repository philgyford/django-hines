/**
 * Add an Array.equals() method for comparing arrays.
 * Via https://stackoverflow.com/a/14853974/250962
 * Usage:
 *  [1,2,3].equals([1,2,3])   // True
 *  [1,2,3].equals([1,2,4])   // False
 */
if (Array.prototype.equals) {
  // Warn if overriding existing method
  console.warn(
    "Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code."
  );
}
// Attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function (array) {
  // If the other array is a falsy value, return
  if (!array) {
    return false;
  }

  // Compare lengths - can save a lot of time
  if (this.length != array.length) {
    return false;
  }

  for (var i = 0, l = this.length; i < l; i++) {
    // Check if we have nested arrays
    if (this[i] instanceof Array && array[i] instanceof Array) {
      // recurse into the nested arrays
      if (!this[i].equals(array[i])) {
        return false;
      }
    } else if (this[i] != array[i]) {
      // Warning - two different object instances will never be equal: {x:20} != {x:20}
      return false;
    }
  }
  return true;
};
// Hide method from for-in loops
Object.defineProperty(Array.prototype, "equals", { enumerable: false });

/**
 * Test if localStorage or sessionStorage is available.
 *
 * Use like:
 *  if (storageAvailable('localStorage')) {
 *    alert('yes');
 *  }
 *
 * Or test for 'sessionStorage'.
 *
 * via https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
 */
function storageAvailable(type) {
  try {
    var storage = window[type],
      x = "__storage_test__";
    storage.setItem(x, x);
    storage.removeItem(x);
    return true;
  } catch (e) {
    return (
      e instanceof DOMException &&
      // everything except Firefox
      (e.code === 22 ||
        // Firefox
        e.code === 1014 ||
        // test name field too, because code might not be present
        // everything except Firefox
        e.name === "QuotaExceededError" ||
        // Firefox
        e.name === "NS_ERROR_DOM_QUOTA_REACHED") &&
      // acknowledge QuotaExceededError only if there's something already stored
      storage.length !== 0
    );
  }
}

/**
 * Utility function.
 * Returns the element indicated by the CSS class name.
 * If there's more than one, returns them all in an HTMLCollection.
 * If there's only one, returns just that one element.
 * If there are none, returns an empty HTMLCollection.
 */
function getElByClass(classname) {
  var el = document.getElementsByClassName(classname);
  if (el && el.length === 1) {
    el = el[0];
  }
  return el;
}

/**
 * Show the element with a CSS class of `classname`.
 */
function showEl(classname) {
  getElByClass(classname).style.display = "";
}

/**
 * Hide the element with a CSS class of `classname`.
 */
function hideEl(classname) {
  getElByClass(classname).style.display = "none";
}

(function () {
  "use strict";

  window.japanese = function module() {
    // Mapping english to japanese characters.
    // Populated by loadCharacters().
    var characters = {
      hiragana: [],
      katakana: [],
    };

    // Will be characters the user has guessed correctly.
    var usedCharacters = [];

    var totalAttempts = 0;

    var correctCount = 0;

    // Will be set to 'hiragana', 'katakana' or 'both':
    var setsToTest = null;

    // The letter displayed to the user to guess at the moment.
    // Will be like ['rya', 'リャ']
    var currentLetter = null;

    var exports = {
      init: function () {
        hideEl("js-alert");
        loadCharacters();
        initListeners();

        // If we have previous progress, dive straight into the test:
        initFromStorage();
      },
    };

    /**
     * All the events we listen for...
     */
    function initListeners() {
      getElByClass("js-startform").addEventListener("submit", handleStart);
      getElByClass("js-guessform").addEventListener("submit", handleGuess);
      getElByClass("js-restart-button").addEventListener(
        "click",
        handleRestartConfirm
      );
      getElByClass("js-restart-link").addEventListener("click", handleRestart);
    }

    /**
     * See if we have any previous progress stored.
     * If so, start the test with the previous progress.
     * Otherwise, do nothing.
     */
    function initFromStorage() {
      if (storageAvailable("localStorage")) {
        var attempts = parseInt(localStorage.getItem("jpTotalAttempts"), 10);
        if (attempts) {
          totalAttempts = attempts;
          correctCount = parseInt(localStorage.getItem("jpCorrectCount"), 10);
          setsToTest = localStorage.getItem("jpSetsToTest");
          usedCharacters = JSON.parse(localStorage.getItem("jpUsedCharacters"));
          startTest();
        }
      }
    }

    /**
     * Store the current progress.
     */
    function storeProgressInStorage() {
      if (storageAvailable("localStorage")) {
        localStorage.setItem("jpTotalAttempts", totalAttempts);
        localStorage.setItem("jpCorrectCount", correctCount);
        localStorage.setItem("jpSetsToTest", setsToTest);
        localStorage.setItem(
          "jpUsedCharacters",
          JSON.stringify(usedCharacters)
        );
      }
    }

    function clearStorage() {
      if (storageAvailable("localStorage")) {
        localStorage.removeItem("jpTotalAttempts");
        localStorage.removeItem("jpCorrectCount");
        localStorage.removeItem("jpSetsToTest");
        localStorage.removeItem("jpCurrentLetter");
        localStorage.removeItem("jpUsedCharacters");
      }
    }

    /**
     * When the initial 'Hiragana and/or Katakana?' checkbox form has been
     * submitted.
     */
    function handleStart(event) {
      event.preventDefault();
      hideMessage();

      setsToTest = null;

      var useHiragana = getElByClass("js-sets-hiragana").checked;
      var useKatakana = getElByClass("js-sets-katakana").checked;

      if (useHiragana && useKatakana) {
        setsToTest = "both";
      } else if (useHiragana) {
        setsToTest = "hiragana";
      } else if (useKatakana) {
        setsToTest = "katakana";
      } else {
        showMessage("Please choose Hiranga and/or Katakana.");
      }

      if (setsToTest !== null) {
        initScores();
        startTest();
      }
    }

    /**
     * Set everything back to the start.
     */
    function initScores() {
      totalAttempts = 0;

      correctCount = 0;

      currentLetter = null;

      usedCharacters = [];

      clearStorage();
    }

    /**
     * Show the guess form and begin the test.
     */
    function startTest() {
      hideEl("js-front");

      showEl("js-quiz");
      showEl("js-instructions");

      updateScoreDisplay();

      showNewLetter();
    }

    /**
     * The user has entered a guess for the current character.
     */
    function handleGuess(event) {
      event.preventDefault();
      hideMessage();

      var guess = getElByClass("js-guessform-input").value;
      guess = guess.toLowerCase().replace(/^\s+|\s+$/g, "");

      var result = checkLetter(guess, currentLetter[0]);

      hideEl("js-instructions");
      showEl("js-answer");

      if (result === "wrong") {
        showEl("js-answer-wrong");
        hideEl("js-answer-pass");
        hideEl("js-answer-correct");
        hideEl("js-answer-letter");

        // For some reason it was losing focus when this happened:
        getElByClass("js-guessform-input").focus();

        totalAttempts += 1;
      } else {
        // 'empty' or 'correct'.
        hideEl("js-answer-wrong");
        showEl("js-answer-letter");

        // Display the answer.
        var romaji = currentLetter[0];
        if (Array.isArray(romaji)) {
          romaji = romaji.join('<span class="text-light">,</span> ');
        }

        getElByClass("js-answer-letter-jp").innerText = currentLetter[1];
        getElByClass("js-answer-letter-en").innerHTML = romaji;

        if (result === "empty") {
          showEl("js-answer-pass");
          hideEl("js-answer-correct");
        } else if (result === "correct") {
          hideEl("js-answer-pass");
          showEl("js-answer-correct");

          totalAttempts += 1;
          correctCount += 1;
          usedCharacters.push(currentLetter);
        }

        // Have they got everything right?
        if (getPercentComplete() === 100) {
          hideEl("js-guessform");
          showEl("js-complete");
          clearStorage();
        } else {
          showNewLetter();
          storeProgressInStorage();
        }
      }

      getElByClass("js-guessform-input").value = "";

      updateScoreDisplay();
    }

    /**
     * The 'Start again' LINK has been clicked.
     * i.e., when the user has completed it all and wants to go again.
     */
    function handleRestart(event) {
      event.preventDefault();

      doRestart();
    }

    /**
     * The 'Start again' BUTTON has been clicked.
     */
    function handleRestartConfirm(event) {
      if (window.confirm("Restarting will erase your score. Are you sure?")) {
        doRestart();
      }
    }

    /**
     * Actually do the restart.
     */
    function doRestart() {
      hideEl("js-quiz");
      hideEl("js-answer");
      hideEl("js-complete");

      showEl("js-guessform");
      showEl("js-front");

      clearStorage();
    }

    /**
     * Update the score display.
     */
    function updateScoreDisplay() {
      getElByClass("js-total-attempts").innerText = totalAttempts;
      getElByClass("js-correct-count").innerText = correctCount;
      getElByClass("js-correct-percentage").innerText = getPercentCorrect();
      var percentComplete = getPercentComplete();
      getElByClass("js-progress-bar").value = percentComplete;
      getElByClass("js-progress-bar").innerText = percentComplete;
    }

    /**
     * Find a new letter to guess and display it.
     */
    function showNewLetter() {
      // Are we going to pick a letter from hiragana or katakana?
      var characterPool = [];

      if (setsToTest === "hiragana") {
        characterPool = characters["hiragana"];
      } else if (setsToTest === "katakana") {
        characterPool = characters["katakana"];
      } else {
        characterPool = characters["hiragana"].concat(characters["katakana"]);
      }

      var letter = "";

      if (characterPool.length - usedCharacters.length === 1) {
        // There's only one letter left to guess, so we have to show that.
        for (var n = 0; n < characterPool.length; n++) {
          if (usedCharacters.indexOf(characterPool[n]) === -1) {
            letter = characterPool[n];
            break;
          }
        }
      } else {
        // Keep picking random letters from the hiragana/katakana arrays
        // until we get one that's not in usedCharacters, and isn't the
        // current (i.e. now previous) letter:
        while (
          usedCharacters.indexOf(letter) > -1 ||
          letter === "" ||
          letter === currentLetter
        ) {
          letter =
            characterPool[Math.floor(Math.random() * characterPool.length)];
        }
      }

      currentLetter = letter;

      getElByClass("js-letter").innerText = letter[1];
      getElByClass("js-guessform-input").focus();
    }

    /**
     * Returns a string of either:
     *  'empty'   - `guess` contains nothing.
     *  'correct' - `guess` matches `answer`.
     *  `wrong`   - `guess` does not match `answer`.
     */
    function checkLetter(guess, answer) {
      if (guess === "") {
        return "empty";
      }

      if (Array.isArray(answer) && answer.indexOf(guess) > -1) {
        // More than one correct answer.
        return "correct";
      } else if (guess === answer) {
        return "correct";
      } else {
        return "wrong";
      }
    }

    /**
     * Returns the percentage of attempts to answer (not passes) that were
     * correct.
     */
    function getPercentCorrect() {
      var percent = 0;
      if (totalAttempts > 0) {
        percent = Math.round((correctCount / totalAttempts) * 100);
      }
      return percent;
    }

    /**
     * Returns the percentage of letters the user has finished correctly so far.
     * i.e. Will be 0 if they've answered nothing, or passed, or got everything
     * wrong.
     * Will be 100 if they've answered all letters correctly, no matter how
     * many passes or incorrect answers along the way.
     */
    function getPercentComplete() {
      var numToGet = 0;

      if (setsToTest === "both" || setsToTest === "hiragana") {
        numToGet += characters["hiragana"].length;
      }

      if (setsToTest === "both" || setsToTest === "katakana") {
        numToGet += characters["katakana"].length;
      }

      var percent = Math.round((correctCount / numToGet) * 100);

      return percent;
    }

    /**
     * Display the text in `msg`.
     */
    function showMessage(msg) {
      getElByClass("js-message").innerText = msg;
      showEl("js-message");
    }

    /**
     * Empty and hide the message element.
     */
    function hideMessage() {
      getElByClass("js-message").innerText = "";
      hideEl("js-message");
    }

    function loadCharacters() {
      // See https://www.nayuki.io/page/variations-on-japanese-romanization
      // for more on Nihon-shiki vs Hepburn romanization.
      characters["hiragana"] = [
        ["a", "あ"],
        ["i", "い"],
        ["u", "う"],
        ["e", "え"],
        ["o", "お"],

        ["ka", "か"],
        ["ki", "き"],
        ["ku", "く"],
        ["ke", "け"],
        ["ko", "こ"],

        ["sa", "さ"],
        [["si", "shi"], "し"],
        ["su", "す"],
        ["se", "せ"],
        ["so", "そ"],

        ["ta", "た"],
        [["ti", "chi"], "ち"],
        [["tu", "tsu"], "つ"],
        ["te", "て"],
        ["to", "と"],

        ["na", "な"],
        ["ni", "に"],
        ["nu", "ぬ"],
        ["ne", "ね"],
        ["no", "の"],

        ["ha", "は"],
        ["hi", "ひ"],
        [["hu", "fu"], "ふ"],
        ["he", "へ"],
        ["ho", "ほ"],

        ["ma", "ま"],
        ["mi", "み"],
        ["mu", "む"],
        ["me", "め"],
        ["mo", "も"],

        ["ya", "や"],
        ["yu", "ゆ"],
        ["yo", "よ"],

        ["ra", "ら"],
        ["ri", "り"],
        ["ru", "る"],
        ["re", "れ"],
        ["ro", "ろ"],

        ["wa", "わ"],
        [["o", "wo"], "を"],

        ["n", "ん"],

        ["ga", "が"],
        ["gi", "ぎ"],
        ["gu", "ぐ"],
        ["ge", "げ"],
        ["go", "ご"],

        ["za", "ざ"],
        [["zi", "ji"], "じ"],
        ["zu", "ず"],
        ["ze", "ぜ"],
        ["zo", "ぞ"],

        ["da", "だ"],
        [["di", "ji", "dji", "dzi"], "ぢ"],
        [["du", "zu", "dzu"], "づ"],
        ["de", "で"],
        ["do", "ど"],

        ["ba", "ば"],
        ["bi", "び"],
        ["bu", "ぶ"],
        ["be", "べ"],
        ["bo", "ぼ"],

        ["pa", "ぱ"],
        ["pi", "ぴ"],
        ["pu", "ぷ"],
        ["pe", "ぺ"],
        ["po", "ぽ"],

        ["kya", "きゃ"],
        ["kyu", "きゅ"],
        ["kyo", "きょ"],

        [["sya", "sha"], "しゃ"],
        [["syu", "shu"], "しゅ"],
        [["syo", "sho"], "しょ"],

        [["tya", "cha"], "ちゃ"],
        [["tyu", "chu"], "ちゅ"],
        [["tyo", "cho"], "ちょ"],

        ["nya", "にゃ"],
        ["nyu", "にゅ"],
        ["nyo", "にょ"],

        ["hya", "ひゃ"],
        ["hyu", "ひゅ"],
        ["hyo", "ひょ"],

        ["mya", "みゃ"],
        ["myu", "みゅ"],
        ["myo", "みょ"],

        ["rya", "りゃ"],
        ["ryu", "りゅ"],
        ["ryo", "りょ"],

        ["gya", "ぎゃ"],
        ["gyu", "ぎゅ"],
        ["gyo", "ぎょ"],

        [["zya", "ja", "jya"], "じゃ"],
        [["zyu", "ju", "jyu"], "じゅ"],
        [["zyo", "jo", "jyo"], "じょ"],

        ["bya", "びゃ"],
        ["byu", "びゅ"],
        ["byo", "びょ"],

        ["pya", "ぴゃ"],
        ["pyu", "ぴゅ"],
        ["pyo", "ぴょ"],

        [["dya", "ja", "dja"], "ぢゃ"],
        [["dyu", "ju", "dju"], "ぢゅ"],
        [["dyo", "jo", "djo"], "ぢょ"],
      ];

      characters["katakana"] = [
        ["a", "ア"],
        ["i", "イ"],
        ["u", "ウ"],
        ["e", "エ"],
        ["o", "オ"],

        ["ka", "カ"],
        ["ki", "キ"],
        ["ku", "ク"],
        ["ke", "ケ"],
        ["ko", "コ"],

        ["sa", "サ"],
        [["si", "shi"], "シ"],
        ["su", "ス"],
        ["se", "セ"],
        ["so", "ソ"],

        ["ta", "タ"],
        [["ti", "chi"], "チ"],
        [["tu", "tsu"], "ツ"],
        ["te", "テ"],
        ["to", "ト"],

        ["na", "ナ"],
        ["ni", "ニ"],
        ["nu", "ヌ"],
        ["ne", "ネ"],
        ["no", "ノ"],

        ["ha", "ハ"],
        ["hi", "ヒ"],
        [["hu", "fu"], "フ"],
        ["he", "ヘ"],
        ["ho", "ホ"],

        ["ma", "マ"],
        ["mi", "ミ"],
        ["mu", "ム"],
        ["me", "メ"],
        ["mo", "モ"],

        ["ya", "ヤ"],
        ["yu", "ユ"],
        ["yo", "ヨ"],

        ["ra", "ラ"],
        ["ri", "リ"],
        ["ru", "ル"],
        ["re", "レ"],
        ["ro", "ロ"],

        ["wa", "ワ"],
        [["o", "wo"], "ヲ"],

        ["n", "ン"],

        ["ga", "ガ"],
        ["gi", "ギ"],
        ["gu", "グ"],
        ["ge", "ゲ"],
        ["go", "ゴ"],

        ["za", "ザ"],
        [["zi", "ji"], "ジ"],
        ["zu", "ズ"],
        ["ze", "ゼ"],
        ["zo", "ゾ"],

        ["da", "ダ"],
        [["di", "ji", "dji", "dzi"], "ヂ"],
        [["du", "zu", "dzu"], "ヅ"],
        ["de", "デ"],
        ["do", "ド"],

        ["ba", "バ"],
        ["bi", "ビ"],
        ["bu", "ブ"],
        ["be", "ベ"],
        ["bo", "ボ"],

        ["pa", "パ"],
        ["pi", "ピ"],
        ["pu", "プ"],
        ["pe", "ペ"],
        ["po", "ポ"],

        ["kya", "キャ"],
        ["kyu", "キュ"],
        ["kyo", "キョ"],

        [["sya", "sha"], "シャ"],
        [["syu", "shu"], "シュ"],
        [["syo", "sho"], "ショ"],

        [["tya", "cha"], "チャ"],
        [["tyu", "chu"], "チュ"],
        [["tyo", "cho"], "チョ"],

        ["nya", "ニャ"],
        ["nyu", "ニュ"],
        ["nyo", "ニョ"],

        ["hya", "ヒャ"],
        ["hyu", "ヒュ"],
        ["hyo", "ヒョ"],

        ["mya", "ミャ"],
        ["myu", "ミュ"],
        ["myo", "ミョ"],

        ["rya", "リャ"],
        ["ryu", "リュ"],
        ["ryo", "リョ"],

        ["gya", "ギャ"],
        ["gyu", "ギュ"],
        ["gyo", "ギョ"],

        [["zya", "ja", "jya"], "ジャ"],
        [["zyu", "ju", "jyu"], "ジュ"],
        [["zyo", "jo", "jyo"], "ジョ"],

        ["bya", "ビャ"],
        ["byu", "ビュ"],
        ["byo", "ビョ"],

        ["pya", "ピャ"],
        ["pyu", "ピュ"],
        ["pyo", "ピョ"],

        [["dya", "ja", "dja"], "ヂャ"],
        [["dyu", "ju", "dju"], "ヂュ"],
        [["dyo", "jo", "djo"], "ヂョ"],

        // ['vu', 'ヴ']
      ];
    }

    return exports;
  };
})();
