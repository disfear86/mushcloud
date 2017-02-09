$(document).ready(function() {
			var currenthtml;
			var latesthtml;

			$.get(window.location.href, function(data) {
				currenthtml = data;
				latesthtml = data;
			});

			setInterval(function() {

				$.get(window.location.href, function(data) {
					latesthtml = data;
				});

				if(currenthtml != latesthtml) {
					location.reload();
				}
			}, 3000);
			});
