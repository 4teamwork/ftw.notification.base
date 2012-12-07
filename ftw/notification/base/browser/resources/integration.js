function initTokenInput(input, pre_select, allow_new) {

  var bhref = $('base').attr('href');
  if (bhref.substr(bhref.length - 1, 1) != '/') {
    bhref += "/";
  }

  var target = $('#' + input);
  console.info(pre_select);

  target.select2({
    placeholder: "Search",
    multiple: true,
    width: '100%',
    minimumInputLength: allow_new && 3 || 0,
    dropdownCssClass: 'bigdrop',
    quietMillis: 500,
    //closeOnSelect: true,
    formatResult: function(item) {
      return item.text;
    },
    createSearchChoice: function(term) {

      if (allow_new) {
        var email_reg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
        if (email_reg.test(term)) {
          return {
            id: term,
            text: term
          };
        }
      }

      return null;
    },
    ajax: {
      url: bhref + 'notification_form/json_source',
      dataType: 'json',
      data: function(term, page) {
        return {
          q: term
        };
      },
      results: function(data, page) {
        return {
          results: data
        };
      }
    }
  });

  // Init values
  target.select2('data', pre_select);


  // Resolve groups
  target.bind('change', function(e) {
    if (e.added !== undefined && e.added.id.substr(0, 6) === 'group:') {
      var recipients = $('#' + input).select2('data');

      // Remove added group
      var remove_idx = recipients.indexOf(e.added);
      recipients.splice(remove_idx, 1);

      // Add group members
      $.getJSON(bhref + 'notification_form/json_source_by_group', {
        'groupid': e.added.id.substr(6)
      }, function(data) {
        $.each(data, function(i, o) {
          recipients.push(o);
        });
        target.select2('data', recipients);
      });
    }

  });
}