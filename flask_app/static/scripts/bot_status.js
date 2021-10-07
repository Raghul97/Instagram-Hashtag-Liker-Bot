function update_task_progress(status_url) {
    $.getJSON(status_url, function(data) {
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if (data['state'] == 'SUCCESS') {
                $('#timer').text("00:00:00");
            }
            else {
                $('#timer').text("Process Failed");
                $("#revoke-task").text('Revoked execution').removeClass("btn-danger").addClass("btn-secondary disabled");
            }
            return
        }
        else {
            if (data['state'] == 'PROGRESS') {
                if (data['items']){
                    $("tbody tr").remove();
                    $("#like-count").text(data['posts_liked']);
                    data['items'].forEach((item) => {
                        $("tbody").append(`<tr>
                        <td><input type="text" class="form-control" value="${item['hashtag']}" disabled></td>
                        <td><input type="text" class="form-control" value="${item['profile_name']}" disabled></td>
                        <td><input type="text" class="form-control" value="${item['post_url']}" disabled></td>
                        </tr>`);
                    });
                }
            }
            setTimeout(function() {
                update_task_progress(status_url);
            }, 2000);
        }
    });
}

function update_timer(status_url) {
    $.getJSON(status_url, function(data) {
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if (data['state'] == 'SUCCESS') {
                $('#timer').text('Finished - ' + data['current_time']);
            }
            else {
                $('#timer').text('Error - ' + data['current_time']);
            }
            return
        }
        else {
            if (data['state'] == 'PROGRESS') {
                $('#timer').text(data['current_time']);
            } else {
                $('#timer').text("08:00:00")
            }
            setTimeout(function() {
                update_timer(status_url);
            }, 1000);
        }
    });
}


$(document).ready(function(){
    $('#timer').text("08:00:00")
    const bot_task_id = $("#bot_task_id").attr("value");
    bot_url = `http://${location.host}/task/status/${bot_task_id}`;
    const timer_id = $("#timer_id").attr("value");
    timer_url = `http://${location.host}/timer/status/${timer_id}`;
    update_task_progress(bot_url);
    update_timer(timer_url);
})

$(document).on('click', "#revoke-task", function () {
    const bot_task_id = $("#bot_task_id").attr("value");
    const timer_id = $("#timer_id").attr("value");
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: `/insta/revoke/execution/${bot_task_id}/${timer_id}`,
        dataType : 'json',
        success : function(data, status, request) {
            $("#revoke-task").text('Revoked execution').removeClass("btn-danger").addClass("btn-secondary disabled");
        },error : function(result){
          console.log("Something went wrong!")
        }
    });
});