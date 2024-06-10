$(document).ready(function () {
    let report_trigger;
    let report_textarea = $("#report-form textarea");
    let report_submit_btn = $("#report-submit-btn");
    let report_type;

    $(document).on("click", "#report-trigger", function () {
        report_textarea.val("");
        report_type = $(this).attr("data-report-type");
        report_trigger = this
    });

    report_submit_btn.on("click", function () {
        let report_content = report_textarea.val();
        if (report_content.trim() === "") {
            show_toast("bg-warning", "提示", "", "内容不能为空");
        } else {
            get_report_info(report_type, report_trigger, report_textarea);
        }
    });

});

function get_report_info(report_type, report_trigger_, report_textarea) {
    let report_trigger = $(report_trigger_);
    let report_content = report_textarea.val();
    console.log(report_content)
    // 1是帖子，2是根回复，3是子回复，4是短评
    let info = []
    if (report_type === "1") {
        let post_id = report_trigger.attr("data-post-id");
        info.push(post_id);
    } else if (report_type === "2") {
        let post_id = report_trigger.attr("data-post-id");
        let root_reply_id = report_trigger.attr("data-root-reply-id");
        info.push(post_id);
        info.push(root_reply_id);
    } else if (report_type === "3") {
        let post_id = report_trigger.attr("data-post-id");
        let root_reply_id = report_trigger.attr("data-root-reply-id");
        let reply_reply_id = report_trigger.attr("data-reply-reply-id");
        info.push(post_id);
        info.push(root_reply_id);
        info.push(reply_reply_id);
    } else if (report_type === "4") {
        let book_id = report_trigger.attr("data-book-id");
        let comment_id = report_trigger.attr("data-comment-id");
        info.push(book_id);
        info.push(comment_id);
    }
    console.log(info)
    send_report(report_type, info, report_content);
}

function send_report(report_type, report_info, report_content) {
    $.ajax({
        url: "/report/",
        method: "post",
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {
            "report_type": report_type,
            "report_info": JSON.stringify(report_info),
            "report_content": report_content
        },
        success: function (res) {
            if (res['success']) {
                show_toast("bg-success-subtle", "提示", "", "举报成功");
                $("#report-modal").modal('hide');
            } else {
                show_toast("bg-warning", "提示", "", "举报失败");
            }
        }
    })
}