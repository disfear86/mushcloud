$(document).ready(function(){
		$('a#del_button').bind('click', function(){
			var del_data = $(this).parents('tr').find('td').first().text().trim();
			if (confirm("Are you sure you want to delete '" + del_data + "'?")) {
				$(this).parents('tr').remove();

			$.ajax({
				  type: "POST",
				  contentType: "application/json; charset=utf-8",
				  url: $SCRIPT_ROOT + "/_delete/",
				  data: JSON.stringify({'data': del_data}),
				  success: function (result) {
				    console.log(result);
				  },
				  dataType: "json"
			});
			}
		});
	});
