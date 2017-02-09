$(document).ready(function() {

    $('#upload').on('submit', function(event) {
        $(".progress").show();
        event.preventDefault();

        var formData = new FormData($('#upload')[0]);
        if (js_folder) {
            var urls = '/home/' + js_folder + '/'
        }
        else {
            var urls = '/home/'
        }

        $.ajax({
            xhr : function() {
                var xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener('progress', function(e) {

                    if (e.lengthComputable) {

                        var percent = Math.round((e.loaded / e.total) * 100);

                        $('#ProgressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
                    }
                });
                return xhr;
            },
            type : 'POST',
            url : urls,
            data : formData,
            processData : false,
            contentType : false,
            success: function () {
              location.reload();
          }
        });
    });
});
