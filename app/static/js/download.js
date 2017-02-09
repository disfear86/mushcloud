$(document).ready(function(){
    $('a#dl_button').bind('click', function(e) {
        var path = '/home/disfear86/Desktop/mushcloud/mushcloud/userfiles/'
        var dl_data = $(this).parents('tr').find('td').first().text().trim();
        if (user) {
            if (js_folder) {
                var file_path = path + user + '/' + js_folder + dl_data;
            }
            else {
                var file_path = path + user + '/' + dl_data
            }
        }
        e.preventDefault();
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/_download/",
              data: JSON.stringify({'data': file_path}),
              success: function (result) {
                console.log(result);
              },
              dataType: "json"
        });
    });
});
