// 书评详情页发表书评

$(document).ready(function () {
    is_login(function (login) {
        if (login) {
            get_comment();
        } else {
            $(".write-comment-btn").attr("data-bs-toggle", "");
            let login_url = $("#navbar-login").attr("href");
            $("#comment-modal").on("show.bs.modal", function (event) {
                event.preventDefault();
                show_toast("text-bg-warning", "错误提示", "", "用户未登录&nbsp;&nbsp;&nbsp;" + "<a href='" + login_url + "'>立即登录</a>");
            });
        }
    });
});

function is_login(callback) {
    $.ajax({
        url: "/user/is_login/",
        method: 'post',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (res) {
            callback(res['is_login'])
        }
    })
}

function get_comment() {
    let send_btn = $("#send-comment-btn");
    send_btn.on("click", function () {
        let comment_input = $("#comment-input");
        let comment = comment_input.val();
        if (!comment.length) {
            show_toast("text-bg-warning", "提示", "", "字数不可以为0");
            return;
        }
        let spilt = window.location.href.split("/");
        let book_id = spilt[spilt.length - 3];
        send_comment(book_id, comment, comment_input)
    });
}

function send_comment(book_id, comment, comment_input) {
    $.ajax({
        url: "/book/comment/" + book_id + "/",
        method: 'post',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        data: {"comment": comment},
        success: function (res) {
            if (res['success']) {
                comment_input.val('');
                location.reload();
                $("#book-comments-wrapper").scrollIntoView();
            } else {
                show_toast("text-bg-warning", "提示", "", res['error']);
            }
        }
    })
}