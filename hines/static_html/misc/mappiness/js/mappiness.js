require.config({
  shim: {
    'jquery.modal': {
      deps: ['jquery'],
      exports: 'jQuery.fn.modal'
    }
  }

  // For development only.
  //urlArgs: "bust=" + (new Date()).getTime()
});


var MAPPINESS_LINE_COLORS = [
  '#FAA43A', // orange
  '#60BD68', // green
  '#5DA5DA', // blue
  '#F17CB0', // pink
  '#B2912F', // brown
  '#B276B2', // purple
  '#DECF3F', // yellow
  '#F15854', // red
  '#4D4D4D'  // gray
];

// From http://blog.mappiness.org.uk/2011/05/23/data-dictionary/
var MAPPINESS_DATA_DICTIONARY = {
  in_out: {in: 'Indoors',
            out: 'Outdoors',
            vehicle: 'In a vehicle'},
  home_work: {home: 'At home',
              work: 'At work',
              other: 'Elsewhere'},
  people: {with_partner: "Spouse, partner, girl/boyfriend",
          with_children: "Children",
          with_relatives: "Other family members",
          with_peers: "Colleagues, classmates",
          with_clients: "Clients, customers",
          with_friends: "Friends",
          with_others: "Other people you know"},
  activities: {do_work: "Working, studying",
              do_meet: "In a meeting, seminar, class",
              do_travel: "Travelling, commuting",
              do_cook: "Cooking, preparing food",
              do_chores: "Housework, chores, DIY",
              do_admin: "Admin, finances, organising",
              do_shop: "Shopping, errands",
              do_wait: "Waiting, queueing",
              do_child: "Childcare, playing with children",
              do_pet: "Pet care, playing with pets",
              do_care: "Care or help for adults",
              do_rest: "Sleeping, resting, relaxing",
              do_sick: "Sick in bed",
              do_pray: "Meditating, religious activities",
              do_wash: "Washing, dressing, grooming",
              do_love: "Intimacy, making love",
              do_chat: "Talking, chatting, socialising",
              do_eat: "Eating, snacking",
              do_caffeine: "Drinking tea/coffee",
              do_booze: "Drinking alcohol",
              do_smoke: "Smoking",
              do_msg: "Texting, email, social media",
              do_net: "Browsing the Internet",
              do_tv: "Watching TV, film",
              do_music: "Listening to music",
              do_speech: "Listening to speech/podcast",
              do_read: "Reading",
              do_theatre: "Theatre, dance, concert",
              do_museum: "Exhibition, museum, library",
              do_match: "Match, sporting event",
              do_walk: "Walking, hiking",
              do_sport: "Sports, running, exercise",
              do_gardening: "Gardening, allotment",
              do_birdwatch: "Birdwatching, nature watching",
              do_hunt: "Hunting, fishing",
              do_compgame: "Computer games, iPhone games",
              do_game: "Other games, puzzles",
              do_bet: "Gambling, betting",
              do_art: "Hobbies, arts, crafts",
              do_sing: "Singing, performing",
              do_other: "Something else",
              do_other2: "Something else"
  }
};

requirejs(['mappiness.controller'],
function (mappiness_controller) {

  mappiness_controller().init({
    lineColors: MAPPINESS_LINE_COLORS,
    dataDictionary: MAPPINESS_DATA_DICTIONARY
  });

});


