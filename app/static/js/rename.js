$(document).ready(function(){
    $("a#ren_button").click(function(){
    	$(this).parents("tr").find("input").toggle();
        var ren_data = $(this).parents('tr').find('td').first().text().trim();
        var mapped = $(this);

        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: $SCRIPT_ROOT + "/_rename/",
              data: JSON.stringify({'data': ren_data}),
              success: function (result) {
                console.log(result);
              },
              dataType: "json"
        });
    });
});
