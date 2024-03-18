$(document).ready(function () {
    post_like();
});

/**
 * 帖子点赞按钮监视
 */
function post_like() {
    let like_btn = $("#post-like-button");
    let unlike_btn = $("#post-unlike-button");
    let like_act, unlike_act;
    like_btn.click(function () {
        like_act = like_btn.hasClass("border-danger-subtle")
        unlike_act = unlike_btn.hasClass("border-danger-subtle")
        if (like_act) {
            remove_style(like_btn, true);
        }
        if (unlike_act) {
            remove_style(unlike_btn, false);
            add_style(like_btn, true);
        }
        if (!like_act && !unlike_act) {
            add_style(like_btn, true);
        }
        send_like_info(true, true, like_act, unlike_act)
    })

    unlike_btn.click(function () {
        like_act = like_btn.hasClass("border-danger-subtle")
        unlike_act = unlike_btn.hasClass("border-danger-subtle")
        if (like_act) {
            remove_style(like_btn, true);
            add_style(unlike_btn, false);
        }
        if (unlike_act) {
            remove_style(unlike_btn, false);
        }
        if (!like_act && !unlike_act) {
            add_style(unlike_btn, false);
        }
        send_like_info(true, false, like_act, unlike_act)
    })
}

/**
 * 添加样式
 * @param btn 点击的按钮
 * @param is_like_btn 是不是like按钮
 */
function add_style(btn, is_like_btn) {
    const _class = "border-danger-subtle";
    btn.addClass(_class);
    let num = parseInt(btn.find("span").text());
    if (!num)
        num = 0;
    btn.find("span").text(num + 1);
    let img = btn.find("img");
    if (is_like_btn) {
        img.attr("src", "/static/img/like_red.svg");
    } else {
        img.attr("src", "/static/img/unlike_red.svg");
    }
}

/**
 * 移除
 * @param btn 点击的按钮
 * @param is_like_btn 是不是like按钮
 */
function remove_style(btn, is_like_btn) {
    const _class = "border-danger-subtle";
    btn.removeClass(_class);
    let num = parseInt(btn.find("span").text());
    num = num - 1;
    let text = num;
    if (num === 0)
        text = ""
    btn.find("span").text(text);
    let img = btn.find("img");
    if (is_like_btn) {
        img.attr("src", "/static/img/like.svg");
    } else {
        img.attr("src", "/static/img/unlike.svg");
    }
}

/**
 * ajax发送点赞数据
 * @param is_post_like 是点击了帖子喜欢按钮，还是点击了评论喜欢按钮
 * @param click_like 是否点击了like按钮
 * @param like_act 点击之前like按钮的状态
 * @param unlike_act 点击之后like按钮的状态
 */
function send_like_info(is_post_like, click_like, like_act, unlike_act) {
    let text = "点踩成功";
    if (click_like)
        text = "点赞成功"
    $.ajax({
        url: window.location.pathname,
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        type: 'post',
        data: {
            'is_post_like': is_post_like,
            'click_like': click_like,
            'like_act': like_act,
            'unlike_act': unlike_act
        },
        success: function (res) {
            // 显示成功提示
            // show_toast("text-bg-primary", "提示", "", text)
        },
        error: function (res) {
            // 显示失败提示
            // show_toast("text-bg-warning", "提示", "", text);
        },
    });
}

// 显示提示消息
function show_toast(head_bg_class, strong_text, small_text, body_text) {
    // 获取提示框的引用
    const toastLive = $("#liveToast");
    // 设置提示框的样式
    toastLive.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
    toastLive.find("strong").text(strong_text);
    toastLive.find("small").text(small_text);
    toastLive.find(".toast-body").text(body_text);
    // 实例化并显示提示框
    const toast = new bootstrap.Toast(toastLive);
    toast.show();
}
