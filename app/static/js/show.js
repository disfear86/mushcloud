$(document).ready(function(){   
    $("a#ren_button").click(function(){
        $(this).parents("tr").find("input").show();
    });
});