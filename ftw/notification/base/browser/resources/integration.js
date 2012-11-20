function initTokenInput(){
  $('#users-to').tokenInput($('base').attr('href') + 'notification_form/json_source', {
      theme: "facebook",
      tokenDelimiter: ",",
      tokenValue: "id",
      propertyToSearch:"name",
      minChars: 2,
      preventDuplicates: true,
      onAdd: function(item){
        $this = $(this);
        $this.closest('.field').removeClass('error');
        console.info(item);
        if (item.id.substr(0, 6) === 'group:'){
          $.getJSON($('base').attr('href') + 'notification_form/json_source_by_group', {'groupid': item.id.substr(6)}, function(data){
            $.each(data, function(i, o){
              $('#users-to').tokenInput("add", {id: o.id, name: o.name});
            });
          });
          $('#users-to').tokenInput("remove", item);
        }

      return false;
      },
      onDelete: function(event){
        $(this).closest('.field').removeClass('error');
      }
      //prePopulate: oldValues

  });

  $(document).keypress(function(e) {
      var value = $("#token-input-users-to").val();
      var trigger = $('#users-to');
      var field = trigger.closest('.field');
      if(e.keyCode == 13) {
        if($("#token-input-users-to").is(":focus")) {
          e.preventDefault();
          if (value.length === 0){
            field.removeClass('error');
            return false;
          }

          var email_reg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
          if(!email_reg.test(value)){
            field.addClass('error');
            return false;
          }
          trigger.tokenInput("add", {id: value, name: value});
          return false;
        }
      }
    });

}


$(function(){
  initTokenInput();
});
