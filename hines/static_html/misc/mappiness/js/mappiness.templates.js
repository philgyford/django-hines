define(['underscore'],
function(_) {
  return function() {
    var exports = {},
        templates = makeTemplates();

    function makeTemplates() {
     var templates = {};

      // FOR UI.KEY.

      // The outline structure for a line's key.
      // Requires line_id and line_color.
      templates.line_key = _.template(' \
        <div id="key-<%= line_id %>" class="key-line" data-line-id="<%= line_id %>"> \
          <p class="key-controls"> \
            <label class="key-show"> \
              <input type="checkbox" class="key-show-control" checked="checked" data-line-id="<%= line_id %>">Show \
            </label> \
            <span class="key-delete key-control"> \
              <span class="sep">•</span> \
              <a href="#" class="key-delete-control" data-line-id="<%= line_id %>">Delete</a> \
            </span> \
            <span class="key-edit key-control"> \
              <span class="sep">•</span> \
              <a href="#" class="key-edit-control" data-line-id="<%= line_id %>">Edit</a> \
            </span> \
            <span class="key-duplicate key-control"> \
              <span class="sep">•</span> \
              <a href="#" class="key-duplicate-control" data-line-id="<%= line_id %>">Duplicate</a> \
            </span> \
          </p> \
          <h2 class="key-title" style="border-top-color: <%= line_color %>;"></h2> \
          <p class="key-no-data text-error">No data matches the constraints below</p> \
          <p class="key-all-data">All responses shown.</p> \
          <div class="key-descriptions"> \
            <div class="key-descriptions-people"></div> \
            <div class="key-descriptions-place"></div> \
            <div class="key-descriptions-activities"></div> \
            <div class="key-descriptions-notes"></div> \
          </div> \
        </div> \
      ');

      // Subtitle for a bit of the key.
      // Requires clss and title.
      templates.line_key_title = _.template(' \
        <h3 class="key-subtitle <%= clss %>"><%= title %></h3> \
      ');

      // A line of text in the key.
      // Requires clss and text.
      templates.line_key_text = _.template(' \
        <p class="<%= clss %>"><%= text %></p> \
      ');

      // One or more rows in the key.
      // Requires clss and a rows array.
      // Each element of rows is an object with description and value elements.
      templates.line_key_rows = _.template(' \
        <ul class="list-unstyled <%= clss %>"> \
          <% _.each(rows, function(row){ %> \
            <li> \
              <span class="key-label"><%= row.description %></span> \
              <span class="key-field"><% if (row.value == 1) { print("✓") } else if (row.value == 0) { print("✕") } else { print(row.value) } %></span> \
            </li> \
          <% }); %> \
        </ul> \
      ');


      // LINE EDITOR.

      templates.line_edit_hidden = _.template(' \
        <div> \
          <input type="hidden" id="le-line-id" value=""> \
          <input type="hidden" id="le-color" value=""> \
        </div> \
      ');

      templates.line_edit_feelings = _.template(' \
        <h2 class="subtitle">Feelings</h2 class="subtitle"> \
        <p class="muted-labels"> \
          <% count = 1; %> \
          <% _.each(feelings, function(description, key) { %> \
            <input type="radio" name="le-feeling" id="le-feeling-<%= key %>" value="<%= key %>"<% if (key == "happy") { print(""); } %>> \
            <label for="le-feeling-<%= key %>"> \
              <%= description %> \
            </label> \
            <% if (count < _.keys(feelings).length) { print("<br>") } %> \
            <% count += 1; %> \
          <% }); %> \
        </p> \
        <hr> \
      ');

      templates.line_edit_people = _.template(' \
        <div id="le-people"> \
          <h2 class="subtitle">People</h2 class="subtitle"> \
          <p class="muted-labels"> \
            <input type="radio" name="le-people" id="le-people-ignore" value="ignore"> \
            <label for="le-people-ignore"> \
              Any \
            </label> \
            <br> \
            <input type="radio" name="le-people" id="le-people-alone" value="alone"> \
            <label for="le-people-alone"> \
              Alone, or with strangers only \
            </label> \
            <br> \
            <input type="radio" name="le-people" id="le-people-with" value="with"> \
            <label for="le-people-with"> \
              With… \
            </label> \
          </p> \
          <ul id="le-people-with-list" class="list-unstyled muted-labels"> \
            <% _.each(people, function(description, key) { %> \
              <li> \
                <label class="le-select-label" for="le-people-<%= key %>"><%= description %></label> \
                <span class="le-select-field"> \
                  <select name="le-people-<%= key %>" id="le-people-<%= key %>"> \
                    <option value="ignore">✓ or ✕</option> \
                    <option value="1">✓</option> \
                    <option value="0">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;✕</option> \
                  </select> \
                </span> \
              </li> \
            <% }); %> \
          </ul> \
        </div> \
        <hr> \
      ');

      templates.line_edit_place = _.template(' \
        <h2 class="subtitle">Place</h2 class="subtitle"> \
        <p> \
          <select name="le-place-inout" id="le-place-inout"> \
            <option value="ignore"><%= _.values(in_out).join(" / ") %></option> \
            <% _.each(in_out, function(description, key) { %> \
              <option value="<%= key %>"><%= description %> only</option> \
            <% }); %> \
          </select> \
          <label for="le-place-inout" class="hide"><%= _.values(in_out).join(" / ") %></label> \
        </p> \
        <p> \
          <select name="le-place-homework" id="le-place-homework"> \
            <option value="ignore"><%= _.values(home_work).join(" / ") %></option> \
            <% _.each(home_work, function(description, key) { %> \
              <option value="<%= key %>"><%= description %> only</option> \
            <% }); %> \
          </select> \
          <label for="le-place-homework" class="hide"><%= _.values(home_work).join(" / ") %></label> \
        </p> \
        <hr> \
      ');

      templates.line_edit_notes = _.template(' \
        <h2 class="subtitle"><label for="le-notes">Notes containing:</label></h2 class="subtitle"> \
        <p> \
          <input type="text" name="le-notes" id="le-notes" value="" placeholder=""> \
        </p> \
        <hr class="le-notes-hr"> \
      ');

      templates.line_edit_activities = _.template(' \
        <div id="le-activities"> \
          <h2 class="subtitle">Activities</h2 class="subtitle"> \
          <div id="le-activities-list"> \
            <ul class="list-unstyled muted-labels"> \
              <% count = 1; %> \
              <% _.each(activities, function(description, key) { %> \
                <% if (key != "do_other2") { %> \
                  <li> \
                    <label class="le-select-label" for="le-activities-<%= key %>"><%= description %></label> \
                    <span class="le-select-field"> \
                      <select name="le-activities" id="le-activities-<%= key %>"> \
                        <option value="ignore">✓ or ✕</option> \
                        <option value="1">✓</option> \
                        <option value="0">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;✕</option> \
                      </select> \
                    </span> \
                  </li> \
                  <% if (count == Math.floor(_.keys(activities).length / 2)) { %> \
                    </ul> \
                    <ul class="list-unstyled muted-labels last"> \
                  <% } %> \
                <% } %> \
                <% count += 1; %> \
              <% }); %> \
            </ul> \
          </div> \
        </div> \
      ');


      // CHART TOOLTIP.

      templates.tooltip = _.template(' \
        <h1><%= start_time %></h1> \
        <p> \
          <span class="label">Happy:</span><span class="field"><%= happy %></span><br> \
          <span class="label">Relaxed:</span><span class="field"><%= relaxed %></span><br> \
          <span class="label">Awake:</span><span class="field"><%= awake %></span> \
        </p> \
        <% if (people.length > 0) { %> \
          <h2>People</h2> \
          <ul class="list-unstyled"> \
            <% _.each(people, function(p){ %> \
              <li><%= p %></li> \
            <% }); %> \
          </ul> \
        <% }; %> \
        <h2>Place</h2> \
        <p> \
          <%= in_out %><br> \
          <%= home_work %> \
        </p> \
        <% if (activities.length > 0) { %> \
          <h2>Activities</h2> \
          <ul class="list-unstyled"> \
            <% _.each(activities, function(a){ %> \
              <li><%= a %></li> \
            <% }); %> \
          </ul> \
        <% }; %> \
        <% if (notes != "") { %> \
          <h2>Notes</h2> \
          <p class="notes"><%= notes %></p> \
        <% }; %> \
      ');

      return templates;
    };


    exports.templates = function(_) {
      if (!arguments.length) return templates;
      templates = _;
      return this;
    };

    return exports;
  };
});
