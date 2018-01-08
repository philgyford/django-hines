/**
 * Generates a JSON-style array of objects emulating Mapiness's JSON file.
 *
 * NOTE: Doesn't generate ALL of the data found in Mappiness's JSON.
 * Only the fields that the rest of the code needs.
 *
 * The data isn't entirely random, but is weighted to try and make a relatively
 * believable persona. Everyone is different and this "person" is just one
 * example. They're less keen on work and meetings than they are on being at
 * home; They tend to eat at regular times and feel a little more tired first
 * thing in the morning and last thing at night; They don't go on holiday or
 * suffer from periods of depression. That kind of thing.
 */
define(['d3'],
function(d3) {
  return function() {
    var exports = {},
        // How far back from today do we generate responses for?
        days = 365,
        responsesPerDay = 2,
        // We'll only generate responses between these hours:
        startHour = 8,
        // Must be higher than startHour. Because.
        endHour = 22;


    /**
     * Returns an array of objects simulating the JSON returned by Mappiness'
     * API.
     */
    exports.getJSON = function() {
      var endDate = new Date();
      // Get the date `days` ago.
      var startDate = new Date(new Date().setDate(endDate.getDate() - days));
      var json = [];
    
      // For every day between startDate and endDate:
      for (var d = startDate; d <= endDate; d.setDate(d.getDate() + 1)) {
        var hours = [];
        while (hours.length < responsesPerDay) {
          // Random hour between startHour and endHour.
          var hour = Math.floor(randomBetween(startHour, endHour+1));
          // Ensure we don't have duplicate hours per day.
          if (hours.indexOf(hour) < 0) {
            hours.push(hour);
          };
        };
        hours = hours.sort(function(a, b){ return a - b; });
        // Get one response for each of the hours we need for this day.
        for (var n = 0; n < hours.length; n++) {
          d.setHours(hours[n]);
          json.push(generateResponse(d, json[json.length-1]));
        };
      };

      return json;
    };

    /**
     * Creates a single response object and returns it.
     * `d` is a Date object.
     * previousResopnse is, if present, the response object generated
     * previously.
     */
     function generateResponse(d, previousResponse) {
      var response = {
        beep_time_epoch: d.getTime(),
        beep_time: formatDate(d),
        start_time_epoch: d.getTime(),
        start_time: formatDate(d)
      };
    
      var place = generatePlace(d);
      response.in_out = place.in_out;
      response.home_work = place.home_work;

      var people = generatePeople(d, place);
      for (p in people) {
        response[p] = people[p];
      };

      var activities = generateActivities(d, response);
      for (a in activities) {
        response[a] = activities[a];
      };

      var feelings = generateFeelings(d, response, previousResponse);
      response.happy   = feelings.happy;
      response.relaxed = feelings.relaxed;
      response.awake   = feelings.awake;

      return response;
    };


    /**
     * Generates the in_out and home_work aspects of a response.
     * `d` is a Date object.
     * Returns an object with in_out and home_work keys.
     */
    function generatePlace(d) {
      var in_out,
          home_work;

      if (isWorkingHours(d)) {
        // At work, maybe.
        var chance = Math.random();
        if (chance < 0.8) {
          home_work = 'work'; 
        } else if (chance < 0.9) {
          home_work = 'home';
        } else {
          home_work = 'other';
        };
      } else if (isWeekend(d)) {
        if (Math.random() < 0.6) {
          home_work = 'home';
        } else {
          home_work = 'other';
        };
      } else {
        // Weekday, outside work hours.
        if (Math.random() < 0.7) {
          home_work = 'home';
        } else {
          home_work = 'other';
        };
      };

      if (isSleepTime(d)) {
        // You should be in bed! No camping apparently.
        in_out = 'in';

      } else if (home_work == 'home') {
        if (Math.random() < 0.8) {
          // If you're at home, you're most likely indoors?
          in_out = 'in'; 
        } else {
          in_out = 'out'; 
        };

      } else if (home_work == 'work') {
        if (Math.random() < 0.9) {
          in_out = 'in';
        } else {
          in_out = 'out'; 
        };

      } else { // 'other'.
        var chance = Math.random();
        if (chance < 0.3) {
          in_out = 'vehicle';
        } else if (chance < 0.6) {
          in_out = 'in';
        } else {
          in_out = 'out'; 
        };
      };

      return {
        in_out: in_out,
        home_work: home_work
      };
    };

    /**
     * Generates all the 1/0 values for people for a response.
     * `place` is the results of generatePlace(), an object with in_out and
     * home_work keys.
     * Returns an object with keys like `with_peers`, `with_partner` etc and
     * values of 1 or 0.
     */
    function generatePeople(d, place) {
      var people = {};

      // Set the default of 0 for everything first:
      for (p in MAPPINESS_DATA_DICTIONARY.people) {
        people[p] = 0;
      };

      if (Math.random() < 0.9) {
        // Because all the below will usually result in being with people, give
        // an overall chance of just not being with anyone.

        if (place.home_work == 'work' ||
            (place.home_work == 'other' && isWorkingHours(d))) {
          if (Math.random() < 0.9) {
            people.with_peers = 1;
          };
          if (Math.random() < 0.2) {
            people.with_clients = 1;
          };
          if (Math.random() < 0.1) {
            people.with_others = 1;
          };
        
        } else if (place.home_work == 'home') {
          if (Math.random() < 0.4) {
            people.with_partner = 1;
          };
          if (Math.random() < 0.4) {
            people.with_children = 1;
          };
          if (Math.random() < 0.2) {
            people.with_relatives = 1;
          };
          if (Math.random() < 0.1) {
            people.with_friends = 1;
          };
          if (Math.random() < 0.1) {
            people.with_others = 1;
          };

        } else { // home_work == 'other', but not working hours.
          if (Math.random() < 0.4) {
            people.with_partner = 1;
          };
          if (Math.random() < 0.4) {
            people.with_children = 1;
          };
          if (Math.random() < 0.2) {
            people.with_relatives = 1;
          };
          if (Math.random() < 0.3) {
            people.with_friends = 1;
          };
          if (Math.random() < 0.2) {
            people.with_others = 1;
          };
        };
      };

      return people;
    };

    /**
     * Generates all the activities for a response.
     * `d` is a Date object.
     * `response` is the response so far, including in_out, home_work,
     * and all the people.
     * Returns an object with keys like 'do_work', 'do_meet' etc and 1 or 0 for
     * each value.
     */
    function generateActivities(d, response) {
      var activities = {};

      // Set the default of 0 for everything first:
      for (a in MAPPINESS_DATA_DICTIONARY.activities) {
        activities[a] = 0;
      };

      if (response.home_work == 'work') {
        // Worky things!
        if (Math.random() < 0.9) { activities.do_work = 1; };

        // Some other probably mutually-exclusive things:
          
        if (response.with_clients == 1) {
          if      (Math.random() < 0.8)  { activities.do_meet = 1; }
          else if (Math.random() < 0.2)  { activities.do_chat = 1; };

        } else if (response.with_peers == 1) {
          if      (Math.random() < 0.4)  { activities.do_meet = 1; }
          else if (Math.random() < 0.1)  { activities.do_chat = 1; };

        } else {
          if      (Math.random() < 0.2)  { activities.do_admin = 1; }
          else if (Math.random() < 0.1)  { activities.do_net = 1; }
          else if (Math.random() < 0.05) { activities.do_compgame = 1; }
          else if (Math.random() < 0.1)  { activities.do_other = 1; };
        };

      } else if (response.home_work == 'home') {

        if (response.with_children == 1 && Math.random() < 0.2) {
          activities.do_childcare = 1;

        } else if (response.with_relative == 1 && Math.random() < 0.2) {
          activities.do_care = 1;

        } else {

          if (
            (response.with_partner == 1 || response.with_friends == 1
            || response.with_relatives == 1 || response.with_children == 1
            || response.with_others == 1)
            && Math.random() < 0.2) {
            activities.do_chat = 1;
          };

          if (activities.do_chat == 0 || Math.random() < 0.3) {
            // If not chatting, you'll be doing one/more of the activities
            // below. If you are chatting, you still might do some.

            // A list of possible things, and combinations of things.
            // More instances of a thing (or combination) mean it's more likely
            // to happen.
            var doings = [
              ['do_tv'], ['do_tv'], ['do_tv', 'do_msg'], ['do_tv', 'do_net'],
              ['do_tv', 'do_msg'], ['do_tv', 'do_msg', 'do_net'],
              ['do_tv', 'do_eat'],
              ['do_music'],
              ['do_read'], ['do_read'], ['do_read', 'do_music'],
              ['do_chores'], ['do_chores', 'do_music'],
              ['do_rest'],
              ['do_cook'], ['do_cook'], ['do_cook', 'do_speech'],
              ['do_cook', 'do_music'],
              ['do_wash'], ['do_wash'],
              ['do_admin'], ['do_admin', 'do_music'],
              ['do_msg'],
              ['do_net'],
              ['do_speech'],
              ['do_gardening'],
              ['do_compgame'],
              ['do_game'],
              ['do_art'],
              ['do_pet'],
              ['do_sport'],
              ['do_work'], ['do_work', 'do_music'],
              ['do_sick']
            ];

            var choice = doings[ randomIntegerBetween(0, doings.length) ];
            for (var n=0; n < choice.length; n++) {
              activities[choice[n]] = 1; 
            };
          };

        };

      } else {
        // Not at home or work.
        
        if (response.in_out == 'vehicle' && Math.random() < 0.7) { 
          activities.do_travel = 1;
        }; 

        // With people:
        if ((response.with_partner == 1 || response.with_relatives == 1
                    || response.with_peers == 1 || response.with_clients == 1
                    || response.with_friends == 1)
                && Math.random() < 0.3) {
          activities.do_chat = 1;
        };

        // More mutually-exclusive activities:

        // Working:
        if (activities.do_chat == 0
            && isWorkingHours(d)
            && (response.with_clients == 1 || response.with_peers == 1)
            && Math.random() < 0.4) {
          activities.do_meet = 1;

        } else {
          if (response.in_out == 'in') {
            var doings = [
              ['do_tv'], ['do_tv', 'do_msg'],
              ['do_theatre'],
              ['do_museum'],
              ['do_work'],
              ['do_shop'], ['do_shop', 'do_msg'],
              ['do_wait', 'do_msg'],
              ['do_pet'],
              ['do_msg'],
              ['do_net'],
              ['do_music'],
              ['do_speech'],
              ['do_read'],
              ['do_match'],
              ['do_sport'],
              ['do_compgame'],
              ['do_game'],
              ['do_bet'],
              ['do_art'],
              ['do_other']
            ];
          
          
          } else if (response.in_out == 'out') {
            var doings = [
              ['do_walk'], ['do_walk'],
              ['do_gardening'],
              ['do_match'],
              ['do_sport'],
              ['do_wait'], ['do_wait', 'do_msg'],
              ['do_pet'],
              ['do_shop'], ['do_shop'], ['do_shop', 'do_msg'],
              ['do_read'],
              ['do_net'],
              ['do_other']
            ];
          
          } else { // In a vehicle.
            var doings = [
              ['do_music'], ['do_music'],
              ['do_other'],
              ['do_read'], ['do_read'],
              ['do_msg'], ['do_msg'],
              ['do_net'],
              ['do_compgame'], ['do_compgame']
            ];
          };
 
          var choice = doings[ randomIntegerBetween(0, doings.length) ];
          for (var n=0; n < choice.length; n++) {
            activities[choice[n]] = 1; 
          };
        };
      };

      // Eating and drink could happen in any location, but is more time
      // dependent.
      var h = d.getHours();

      // Drinking.
      if (h <= 17) {
        if (Math.random() < 0.08) { activities.do_caffeine = 1; };
      };
      if (response.home_work !== 'work' && activities.do_caffeine !== 1) {
        if (h >= 12 && h <= 17) {
          if (Math.random() < 0.05) { activities.do_booze = 1; };
        } else if (h >= 18) {
          if (Math.random() < 0.2) { activities.do_booze = 1; };
        };
      };
      if ((h >= 6 && h <= 8) || (h >= 12 && h <= 14) || (h >= 19 && h <= 21)) {
        if (Math.random() < 0.5) { activities.do_eat = 1; };
      };

      // Ensure there's at least one activity checked.

      var doingSomething = false;
      for (a in activities) {
        if (activities[a] == 1) {
          doingSomething = true;
        };
      };
      if (doingSomething == false) { activities.do_other = 1; };

      return activities; 
    };


    /**
     * Returns an object with keys of `happy`, `relaxed` and `awake`, each with
     * a value from 0 to 1.
     * `response` is all the response data so far (people, activities, in_out,
     * home_work).
     * `previousResponse` is either undefined, or is, er, the set of response
     * data before this one.
     *
     * NOTE: This is just one entirely made-up persona of how one person might
     * feel about particular activities or situations. I'm not suggesting
     * everyone feels like this, or I feel like this, or anyone should feel
     * like this. It's an off-the-top-of-my-head imagining of some factors that
     * will create some not-random changes to the data which will make it more
     * interesting.
     */
    function generateFeelings(d, response, previousResponse) {
      // Base feelings that may get adjusted...
      // We use three random numbers per feeling so that the total is weighted
      // towards the centre of the range.
      // The different feelings have different amounts of adjustments later, so
      // we start with different possible totals here.
      var feelings = {
        happy:   randomBetween(0.05, 0.25) +
                 randomBetween(0.05, 0.25) +
                 randomBetween(0.05, 0.25),

        relaxed: randomBetween(0.00, 0.35) +
                 randomBetween(0.05, 0.40) +
                 randomBetween(0.00, 0.30),

        awake:   randomBetween(0.00, 0.35) +
                 randomBetween(0.05, 0.40) +
                 randomBetween(0.00, 0.30)
      };

      // Alter for people and activities.

      // Any of these keys in response being 1 will add the adjustment.
      var happyWeightings = {
        with_partner:    0.1,
        with_children:   0.1,
        with_clients:   -0.1,
        with_friends:    0.15,
        do_work:        -0.1,
        do_meeting:     -0.1, // Probably as well as do_work.
        do_cook:         0.05,
        do_chores:      -0.1,
        do_admin:       -0.05,
        do_sick:        -0.3,
        do_chat:         0.15,
        do_tv:           0.05,
        do_theatre:      0.05,
        do_museum:       0.05,
        do_match:        0.1,
        do_sport:        0.1,
        do_gardening:    0.1,
        do_birdwatch:    0.1,
        do_art:          0.1,
        do_sing:         0.1
      };

      var relaxedWeightings = {
        with_peers:     -0.03,
        with_clients:   -0.1,
        do_meeting:     -0.1,
        do_wait:        -0.05,
        do_sick:        -0.1,
        do_childcare:   -0.15,
        do_care:        -0.15,
        do_pray:         0.1,
        do_alchohol:     0.1,
        do_tv:           0.05,
        do_gardening:    0.05,
        do_art:          0.05,
        do_sing:         0.05
      };

      var awakeWeightings = {
        do_rest:        -0.1,
        do_sick:        -0.25,
        do_sport:        0.15,
        do_birdwatch:    0.05
      };

      for (k in response) {
        if (response[k] == 1) {
          if (k in happyWeightings) {
            feelings.happy += happyWeightings[k]; 
          };
          if (k in relaxedWeightings) {
            feelings.relaxed += relaxedWeightings[k]; 
          };
          if (k in awakeWeightings) {
            feelings.awake += awakeWeightings[k]; 
          };
        };
      };

      // Alter for time of day.
      // Sleepier at start and end of day.
      if (d.getHours() < 7 || d.getHours > 22) {
        feelings.awake -= 0.1; 
      } else if (d.getHours() < 8 || d.getHours > 21) {
        feelings.awake -= 0.05; 
      };
      
      // Alter for previous response.
      // Sometimes, feelings just hang around don't they.
      if (previousResponse != undefined) {
        if (previousResponse.happy < feelings.happy) {
          feelings.happy -= 0.05; 
        } else if (previousResponse.happy > feelings.happy) {
          feelings.happy += 0.05; 
        };
      };

      // Alter for in/out, home/work.
      if (response.in_out == 'out') {
        // S/he likes outside.
        feelings.happy += 0.05;
        feelings.relaxed += 0.05;
        feelings.awake += 0.05;
      };
      if (response.home_work == 'home') {
        feelings.relaxed += 0.05;
      } else if (response.home_work == 'work') {
        feelings.relaxed -= 0.05;
      };

      // Adjust relaxed based on happy?
      // No - they seem to vaguely follow each other anyway.

      // Clamp.
      // If a feeling is above 1 or below 0, ensure it's randomly within
      // bounds.
      for (f in feelings) {
        if (feelings[f] >= 1) {
          var difference = feelings[f] - 1;
          feelings[f] -= randomBetween( (difference + 0.01), (difference + 0.04) );

        } else if (feelings[f] <= 0) {
          var difference = Math.abs(feelings[f]);
          feelings[f] += randomBetween( (difference + 0.01), (difference + 0.03) );
        };
      };

      return feelings;
    };
    
    /**
     * Returns a random float between min and max.
     */
    function randomBetween(min, max) {
      return Math.random() * (max - min) + min;
    };

    /**
     * Returns a random integer between min and max.
     */
    function randomIntegerBetween(min, max) {
      return Math.floor(Math.random() * (max - min)) + min;
    };

    /**
     * Is a datetime within what we're calling working hours?
     * `d` is a Date object.
     * Returns boolean.
     */
    function isWorkingHours(d) {
      var day = d.getDay(),
          hours = d.getHours();

      if (day > 0 && day < 6 && hours >= 9 && hours <= 17) {
        return true;
      } else {
        return false;
      };
    };

    /**
     * Is a datetime on a Saturday or Sunday? 
     * `d` is a Date object.
     * Returns boolean.
     */
    function isWeekend(d) {
      var day = d.getDay();
      if (day == 0 || day == 7) {
        return true;
      } else {
        return false;
      };
    };

    /**
     * Is a datetime during what we're calling hours you're asleep? 
     * `d` is a Date object.
     * Returns boolean.
     */
    function isSleepTime(d) {
      var hours = d.getHours();
    
      if (hours <= 7 || hours >= 23) {
        return true;
      } else {
        return false;
      };
    };

    /**
     * Returns a string representing a date/time in the format
     * 2011/03/13 12:11:26 +0100 
     * d is a Date object.
     */
    function formatDate(d) {
      // Add a leading 0 if n is less than 10.
      var fixNum = function(n) {
        return (n < 10 ? '0' : '') + n;
      };

      // Given a Date.getTimezoneOffset(), returns a string like '+0100'.
      var formatTZ = function(offset) {
        return (-offset < 0 ? '-' : '+') +
              fixNum(Math.abs(offset / 60)) +
              '00'; 
      };

      return d.getFullYear() + '/' + 
             fixNum(d.getMonth() + 1) + '/' +
             fixNum(d.getDate()) + ' ' +
             fixNum(d.getHours()) + ':' +
             fixNum(d.getMinutes()) + ':' +
             fixNum(d.getSeconds()) + ' ' +
             formatTZ(d.getTimezoneOffset());
    };

    exports.days = function(_) {
      if (!arguments.length) return days;
      days = _;
      return this;
    };

    exports.responsesPerDay = function(_) {
      if (!arguments.length) return responsesPerDay;
      responsesPerDay = _;
      return this;
    };

    exports.startHour = function(_) {
      if (!arguments.length) return startHour;
      startHour = _;
      return this;
    };

    exports.endHour = function(_) {
      if (!arguments.length) return endHour;
      endHour = _;
      return this;
    };

    return exports;
  };
});

