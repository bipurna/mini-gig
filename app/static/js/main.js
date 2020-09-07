$(document).ready(function () {

    $('.likebtn').on('click',function(){
        var post_id = $(this).attr('post_id');
        req = $.ajax({
            url: '/like/'+post_id,
            type:'POST',
            data :{post_id:post_id,likes:likes}
        })
        .done(function(data){
            $("#count"+post_id).text(data.likes);
        });
    });
    $('.deletebtn').on('click', function () {
        var post_id = $(this).attr('post_id');
        event.preventDefault();
       
        $.ajax({
            url: '/delete/' + post_id,
            type: 'POST',
            data:{
                post_id:post_id
            },
            success: function (data) {
                if (data.success == 1) {
                    $("#msg").text("Data deleted successfully").show();
                } else {
                    $("#msg").text("There is problems deleting post").show();
                }
            },
            error: function () {
                $("#msg").text("Problems occurs!").show();
            }
        })
        .done(function () {
            location.reload();
        });
        
    });
    $('.deletecmt').on('click', function () {
        var cmt_id = $(this).attr('cmt_id');
        event.preventDefault();
        $.ajax({
            url: '/delete-comment/' + cmt_id,
            type: 'POST',
            data: {
                cmt_id: cmt_id
            },
            success: function (data) {
                if (data.success == 1) {
                    $("#msg").text("Data deleted successfully").show();
                } else {
                    $("#msg").text("There is problems deleting post").show();
                }
            },
            error: function () {
                $("#msg").text("Problems occurs!").show();
            }
        })
            .done(function () {
                location.reload();
            });

    });
    $('.post').on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            data:{
                post:$('.postin').val(),
                user_id:$(this).attr('user_id')
            },
            type: 'POST',
            url: '/posts',
            success: function(data){
                if (data.success==1){
                    $("#msg").text("Data Submited Successfully!").show();
                }else{
                    $("#msg").text("There is problems adding post").show();
                }
            },
            error:function(){
                $("#msg").text("Problems occurs!").show();
            }
            

        })
        .done(function (){
            location.reload();
        });
        
        
        
    });
    $('.reply_btn').on('submit', function (event) {
        var post_id= $(this).attr('post_id');

        
        $.ajax({
            data: {
                reply: $('.replyin').val(),
                post_id:post_id
            },
            type: 'POST',
            url: '/reply/'+post_id,
            success: function (data) {
                if (data.success == 1) {
                    $("#msg").text("comment added successfully").show();
                    
                } else {
                    $("#msg").text("There is problems commenting the post").show();
                }
            },
            error: function () {
                $("#msg").text("Problems occurs!").show();
            }
        })
            .done(function () {
                location.reload();
                
            });
        event.preventDefault(); 
        
    });
    
    $('#action_menu_btn').click(function () {
        $('.action_menu').toggle();
    });
    $(document).on('change', '.custom-file-input', function (event) {
        $(this).next('.custom-file-label').html(event.target.files[0].name);
    })
    $('#postModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var recipient = button.data('post'); // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var modal = $(this);
        
        modal.find('.modal-body textarea').val(recipient);
    });
       $('#commentModal').on('show.bs.modal', function (event) {
           var button = $(event.relatedTarget); // Button that triggered the modal
           var recipient = button.data('post'); // Extract info from data-* attributes
           // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
           // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
           var modal = $(this);

           modal.find('.modal-body textarea').val(recipient);
       });
    $(function () {
        $('#reply').on('keyup paste', function () {
            var $el = $(this),
                offset = $el.innerHeight() - $el.height();

            if ($el.innerHeight() < this.scrollHeight) {
                // Grow the field if scroll height is smaller
                $el.height(this.scrollHeight - offset);
            } else {
                // Shrink the field and then re-set it to the scroll height in case it needs to shrink
                $el.height(1);
                $el.height(this.scrollHeight - offset);
            }
        });
    });
});
setTimeout(function () {
    jQuery('.flash').fadeOut('fast');
}, 30000);