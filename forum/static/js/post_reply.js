let href_split = location.href.split("/");
let post_id = href_split[href_split.length - 2];
var page = 0

$(document).ready(function () {
    // const scrollTop = window.scrollY || document.documentElement.scrollTop;
    // const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    // const documentHeight = document.documentElement.scrollHeight;
    // console.log(scrollTop)
    // console.log(windowHeight)
    // console.log(documentHeight)
    checkUserLogin().then(function (is_login) {
        if (!is_login) {
            $(".top-reply-input-wrapper textarea").attr("disabled", "").attr("placeholder", "请登录后再来哦~");
            $(document).on('click', '.reply-trigger', function (event) {
                let login_url = $("#navbar-login").attr("href");
                show_toast("text-bg-warning", "错误提示", "", "用户未登录&nbsp;&nbsp;&nbsp;" + "<a href='" + login_url + "'>立即登录</a>");
            });
        }
    });

    $(".top-reply-input-wrapper button").on("click", function () {
        let textarea = $(".top-reply-input-wrapper textarea");
        send_reply(textarea.val(), null, null, textarea);
    })

    window.addEventListener('scroll', function () {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const documentHeight = document.documentElement.scrollHeight;
        // console.log(scrollTop)
        // console.log(windowHeight)
        // console.log(documentHeight)
        if (scrollTop + windowHeight >= documentHeight - 1) {
            load_post_reply_page();
        }
        // let reply_all = $("#reply-all")
        // let element_offset = reply_all.offset();
        // let element_height = reply_all.outerHeight();
        // let window_height = $(window).height();
        // let scroll_top = $(window).scrollTop();
        // let element_bottom = element_offset.top + element_height;
        //
        // if ((element_bottom >= scroll_top) && (element_bottom <= (scroll_top + window_height))) {
        //     load_post_reply_page();
        // }

    });
    load_post_reply_page();
});

function isElementFullyInViewport(el) {
    // 获取元素的边界框
    var rect = el.getBoundingClientRect();

    // 获取视口的高度和宽度
    var windowHeight = (window.innerHeight || document.documentElement.clientHeight);
    var windowWidth = (window.innerWidth || document.documentElement.clientWidth);

    // 判断元素是否完全在视口内
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= windowHeight &&
        rect.right <= windowWidth
    );
}

function load_post_reply_page() {
    page += 1;
    $.ajax({
        url: "reply/",
        method: 'get',
        data: {
            "page": page,
        },
        success: function (replies) {
            if (replies) {
                console.log(replies)
                for (const reply of replies) {
                    let reply_block = construct_reply(reply['avatar_url'], reply['username'], reply['content'], reply['reply_time'], reply['user_id'], reply['id']);
                    $("#reply-all").append(reply_block);
                    let reply_reply_wrapper = reply_block.find(".reply-reply-wrapper");
                    let replies_of_reply = reply['reply'];
                    if (replies_of_reply) {
                        for (const reply_of_reply of replies_of_reply) {
                            let reply_reply_block = construct_reply_reply(reply_of_reply['avatar_url'], reply_of_reply['username'], reply_of_reply["content"], reply_of_reply['reply_time'], reply_of_reply["user_id"], reply_of_reply['reply_to'], reply_of_reply['id']);
                            reply_reply_wrapper.append(reply_reply_block);
                        }
                    }
                    if (reply['has_more']) {
                        let more_reply_btn = construct_more_reply_btn();
                        reply_block.find(".content-wrapper").append(more_reply_btn);
                        more_reply_btn.on("click", function () {
                            load_reply_reply_page(reply_block, reply['id'], 0)
                            $(this).remove();
                        });
                    }
                }
            }
        }
    });
}

function load_reply_reply_page(reply_block, root_reply_id, page) {
    $.ajax({
        url: window.location.pathname + "reply/" + root_reply_id + "/",
        method: "get",
        data: {
            "page": page,
        },
        success: function (data) {
            console.log(data)
            let replies = data['replies'];
            let has_previous = data['has_previous'];
            let has_next = data['has_next'];
            let page_now_ = data['page_now'];

            let reply_reply_wrapper = reply_block.find(".reply-reply-wrapper");
            reply_reply_wrapper.empty();

            for (const reply of replies) {
                let reply_reply_block = construct_reply_reply(reply['avatar_url'], reply['username'], reply["content"], reply['reply_time'], reply["user_id"], reply['reply_to'], reply['id'])
                reply_reply_wrapper.append(reply_reply_block);
            }
            let paginator_wrapper = $("<div>").addClass("reply-paginator");
            let previous = $("<span>").text("上一页");
            let page_now = $("<span>").addClass("no-hover").text(page_now_);
            let next = $("<span>").text("下一页");

            if (has_previous) {
                previous.attr("page", page_now_ - 1);
                previous.on("click", function () {
                    load_reply_reply_page(reply_block, root_reply_id, page_now_ - 1);
                });
            } else {
                previous.addClass("opacity-50 no-hover").attr("id", "previous-page");
            }
            if (has_next) {
                next.attr("page", page_now_ + 1);
                next.on("click", function () {
                    load_reply_reply_page(reply_block, root_reply_id, page_now_ + 1);
                });
            } else {
                next.addClass("opacity-50 no-hover").attr("id", "next-page");
            }

            paginator_wrapper.append(previous, page_now, next);
            reply_reply_wrapper.append(paginator_wrapper);
        }
    });
}

function construct_reply(avatar_, username_, content_, reply_time_, user_id, reply_id) {
    if (avatar_ === undefined || avatar_ === null || avatar_ === "") {
        avatar_ = "/static/img/default_avatar.svg";
    }

    let reply_block = $("<div>").addClass("ms-4 mt-3 border-bottom reply-block").attr("reply-id", reply_id);
    let flex_container = $("<div>").addClass("d-flex align-items-start");
    let avatar = $("<img>").attr("id", "avatar-large");
    let content_wrapper = $("<div>").addClass("ms-4 pb-3 flex-grow-1 content-wrapper");
    let username = $("<a>").addClass("text-decoration-none text-dark-emphasis reply-username").attr("href", "/user/userinfo/" + username_ + '/');
    let content = $("<div>").addClass("mt-2");
    let reply_info_wrapper = $("<div>").addClass("text-black-50 mt-1 reply-info-wrapper");
    let reply_time = $("<span>")
    let reply_trigger = $("<span>").addClass("ms-2 text-decoration-none reply-trigger").attr("reply-id", reply_id).attr("username", username_).text("回复").on('click', function () {
        reply_trigger_on_click(this);
    });
    let reply_reply_wrapper = $("<div>").addClass("reply-reply-wrapper");

    reply_block.attr("user-id", user_id);
    avatar.attr("src", avatar_);
    username.text(username_);
    content.text(content_);
    reply_time.text(reply_time_);

    reply_info_wrapper.append(reply_time, reply_trigger);
    content_wrapper.append(username, content, reply_info_wrapper, reply_reply_wrapper);
    flex_container.append(avatar, content_wrapper);
    reply_block.append(flex_container);

    return reply_block;
}

function reply_trigger_on_click(trigger_) {
    let trigger = $(trigger_);
    checkUserLogin().then(function (is_login) {
        if (!is_login) {
            trigger.on('click', function () {
                let login_url = $("#navbar-login").attr("href");
                show_toast("text-bg-warning", "错误提示", "", "用户未登录&nbsp;&nbsp;&nbsp;" + "<a href='" + login_url + "'>立即登录</a>");
            });
        } else {
            add_reply_input(trigger_);
        }
    });
}

function construct_reply_reply(avatar_, username_, content_, reply_time_, user_id, reply_to, reply_id) {
    if (avatar_ === undefined || avatar_ === null || avatar_ === "") {
        avatar_ = "/static/img/default_avatar.svg";
    }

    let reply_reply_block = $("<div>").addClass("mt-2");
    let flex_container = $("<div>").addClass("d-flex align-items-start");
    let avatar = $("<img>").attr("id", "avatar-mini");
    let content_wrapper = $("<div>").addClass("ms-3");
    let username = $("<a>").addClass("text-decoration-none text-dark-emphasis reply-username").attr("href", "/user/userinfo/" + username_ + '/');
    let content = $("<span>").addClass("ms-2");
    let reply_info_wrapper = $("<div>").addClass("text-black-50 mt-1 reply-info-wrapper");
    let reply_time = $("<span>");
    let reply_trigger = $("<span>").addClass("ms-2 text-decoration-none reply-trigger").attr("reply-id", reply_id).attr("username", username_).text("回复").on("click", function () {
        reply_trigger_on_click(this);
    });

    reply_reply_block.attr("user-id", user_id);
    avatar.attr("src", avatar_);
    username.text(username_);
    content.text(content_);
    reply_time.text(reply_time_);

    reply_info_wrapper.append(reply_time, reply_trigger);
    if (reply_to) {
        let span = $("<span>").addClass("ms-2").text("回复");
        let reply_to_user = $("<a>").addClass("text-decoration-none ms-1").attr("href", "/user/userinfo/" + username_ + "/").text("@" + reply_to['username'] + ":");
        content_wrapper.append(username, span, reply_to_user, content, reply_info_wrapper);
    } else {
        content_wrapper.append(username, content, reply_info_wrapper);
    }
    flex_container.append(avatar, content_wrapper);
    reply_reply_block.append(flex_container);

    return reply_reply_block;
}

function construct_more_reply_btn() {
    return $("<span>").addClass("text-decoration-none more-reply-trigger").text("查看更多回复")
}

function add_reply_input(trigger_) {
    remove_input_reply();
    console.log("开启")
    let trigger = $(trigger_);
    let username = trigger.attr("username");
    let reply_to = trigger.attr("reply-id");
    let content_wrapper = trigger.closest(".content-wrapper");

    let reply_wrapper = $("<div>").addClass("mt-4 ms-4 reply-input-wrapper");
    let flex_container = $("<div>").addClass("d-flex align-items-start");
    let avatar = $("<img>").attr("id", "avatar-large").attr("src", $(".top-reply-input-wrapper img").attr("src"))
    let textarea = $("<textarea>").addClass("form-control ms-4").attr("rows", "2").attr("placeholder", "回复@" + username).css("height", "44px");
    let submit_btn_wrapper = $("<div>").addClass("reply-submit-wrapper");
    let submit_btn = $("<button>").addClass("btn btn-sm btn-outline-primary float-end mt-3 px-3").text("发表")
    submit_btn.on("click", function () {
        let root_reply_id = $(this).closest(".content-wrapper").find(".reply-trigger").eq(0).attr("reply-id");
        let textarea = $(this).closest(".reply-input-wrapper").find("textarea")
        send_reply(textarea.val(), root_reply_id, reply_to, textarea);
    })

    submit_btn_wrapper.append(submit_btn);
    flex_container.append(avatar, textarea);
    reply_wrapper.append(flex_container, submit_btn_wrapper);

    content_wrapper.append(reply_wrapper);

    // 再次点击该按钮后会关闭回复框
    trigger.off("click");
    trigger.on("click", function () {
        $(this).off("click");
        remove_input_reply();
    });
}

function send_reply(content, root_reply_id, reply_to, textarea) {
    console.log(content)
    console.log(root_reply_id)
    console.log(reply_to)
    if (content.trim() === "") {
        show_toast("text-bg-warning", "错误提示", "", "回复不能为空~");
    } else {
        $.ajax({
            url: window.location.pathname + "reply/",
            method: 'post',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            data: {
                "content": content,
                "root_reply_id": root_reply_id,
                "reply_to": reply_to
            },
            success: function (data) {
                if (data['success']) {
                    const reply = data['reply']
                    console.log(reply);
                    show_toast("text-bg-success", "提示", "", "发表成功");
                    textarea.val("");
                    remove_input_reply();
                    if (root_reply_id) {
                        let selector = '[reply-id="' + root_reply_id + '"]'
                        $(selector).find(".reply-reply-wrapper").append(construct_reply_reply(
                            reply['avatar_url'], reply['username'], reply['content'], reply['reply_time'], reply['user_id'], reply['reply_to'], reply['id']
                        ));
                    } else {
                        $("#reply-all").prepend(
                            construct_reply(
                                reply['avatar_url'], reply['username'], reply['content'], reply['reply_time'], reply['user_id'], reply['id']
                            )
                        )
                    }
                } else {
                    show_toast("text-bg-warning", "错误提示", "", data['error']);
                }
            }
        });
    }
}

function remove_input_reply() {
    console.log("关闭全部");
    $(".reply-trigger").off("click")
    $(".reply-trigger").on("click", function () {
        reply_trigger_on_click(this);
    })
    $(".reply-input-wrapper:not(.top-reply-input-wrapper)").remove();
}