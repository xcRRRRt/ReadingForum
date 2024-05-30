$(document).ready(function () {
    $(".django-ckeditor-widget").css({'width': '100%'});
    CKEDITOR.instances.id_content.on("instanceReady", function () {
        $("#cke_1_contents").css("height", "500px");
    });
    $("#bound-book").hide();
    bind_book();
    cancel_bind();

    // 文章标签
    let labels_all = $("#labels-chosen");
    labels_all.on("click", "button", function () {
        $(this).parent().remove();
    });
    $("#label-add").click(add_label);

    // 提交表单
    submit_form();
})

function toggle_submit_btn() {
    let submit_btn = $("#ckeditor-submit");

    let spinner = submit_btn.children().eq(0);
    let text = submit_btn.children().eq(1);

    spinner.toggle(); // 切换 spinner 的显示状态
    if (text.text() === "发布") {
        text.text("正在发布");
        submit_btn.prop('disabled', true);
    } else {
        text.text("发布");
        submit_btn.prop('disabled', false);
    }
}


function submit_form() {
    let form = $("#ckeditor-form");
    // 发布文章
    $("#ckeditor-submit").click(function (event) {
        event.preventDefault();
        for (let instance in CKEDITOR.instances) {
            CKEDITOR.instances[instance].updateElement();
        }
        // 标题
        let title_input = $("#editor-post-title");
        let title = title_input.val().trim();
        if (title.length < 5 || title.length > 30) {
            title_input.attr("class", "form-control is-invalid");
            title_input.next().text("应在5-50个字符之间(当前字符数" + title.length + ")")
            return;
        }

        toggle_submit_btn();


        title_input.attr("class", "form-control");
        $("#id_title").val(title);
        // 标签
        let labels = ""
        $("#labels-chosen span").each(function () {
            labels += $(this).text() + " "
        })
        labels = labels.trim();
        $("#id_labels").val(labels);
        // 绑定书籍
        let href = $("#bound-book a").attr("href");
        if (href) {
            let href_split = href.split("/");
            $("#id_bound_book").val(href_split[href_split.length - 2]);
        }

        $.ajax({
            url: form.attr("action"),
            type: form.attr("method"),
            data: form.serialize(),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (res) {
                if (res['success']) {
                    // alert(generate_toast_url("/", "bg-success", "发布成功", "", "帖子发布成功"))
                    window.location.href = generate_toast_url("/", "bg-success", "发布成功", "", "帖子发布成功");
                    // window.location.href = "/?show_toast=true&head_bg_class=bg-success&strong_text=发布成功&body_text=帖子发布成功";
                } else {
                    console.log(res)
                    toggle_submit_btn();
                    let errors = res['errors'];
                    let content_with_hint = res['content_with_hint'];
                    replace_content(content_with_hint);
                    let content_errors = errors['content'];
                    show_errors(content_errors);
                }
            },
        });

        // $("#ckeditor-form").submit();
    });
}

// 妈妈呀终于放上去了
function replace_content(new_content) {
    if (new_content) {
        CKEDITOR.instances['id_content'].setData(new_content);
        let doc = $("iframe")[0].contentWindow.document
        let content = $(doc).find("body");
        content.html(new_content);
        let sensitive_words = content.find(".sensitive-word")
        sensitive_words.css({"opacity": 1});
        sensitive_words.each(function (index, elem) {
            blink(elem);
        })
    }
}

function blink(elem) {
    $(elem).fadeOut(500, function () {
        $(this).fadeIn(500, function () {
            blink(elem); // 循环调用blink函数
        });
    });
}

function show_errors(errors) {
    for (let i = 0; i < errors.length; i++) {
        show_toast("text-bg-warning", "提示", "", errors[i])
    }
}

function add_label() {
    let input = $("#label-add").prev();
    let input_val = input.val();
    if (input_val.trim().length !== 0) {
        if ($("#labels-chosen div").length >= 6) {
            show_toast("text-bg-warning", "提示", "", "标签太多啦！");
            return;
        }
        const label = $("<div class=\"border rounded-pill px-2 bg-secondary-subtle me-2 mb-2\"></div>");
        const remove = $("<button type='button'>×</button>");
        const span = $("<span></span>");
        span.text(input_val);
        label.append(span, remove);
        $("#labels-chosen").append(label);
        input.val("");
    }
}

function bind_book() {
    let book_bind_fake = $('#book-bind-fake');
    let book_bind_real = $('#book-bind');
    let search_dropdown = $('#searchDropdown');

    function adjustDropdownWidth() {
        search_dropdown.css('width', book_bind_fake.outerWidth());
    }

    // Adjust the dropdown width on page load and window resize
    adjustDropdownWidth();
    $(window).resize(adjustDropdownWidth);

    book_bind_fake.focus(function () {
        search_dropdown.show();
        book_bind_real.focus();
        book_bind_fake.hide();
    });

    book_bind_real.blur(function () {
        setTimeout(function () {
            search_dropdown.hide();
            book_bind_fake.show();
        }, 200);
    });

    book_bind_real.on('input', function () {
        const query = $(this).val();
        clear_dropdown();
        if (query.length > 0) {
            query_book(query)
        }
    })
}


function query_book(query) {
    $.ajax({
        url: '/editor/search-book/',
        method: 'get',
        data: {
            'q': query
        },
        success: function (res) {
            let books = res['books'];
            add_book_to_dropdown(books);
        }
    })
}

function clear_dropdown() {
    let wrapper = $("#searchDropdown div");
    wrapper.empty();
}

function add_book_to_dropdown(books) {
    let wrapper = $("#searchDropdown > div");
    for (const book of books) {
        // 创建 dropdown-item-container div
        let $dropdownItemContainer = $('<div>', {
            class: 'dropdown-item-container py-1 px-2 rounded-3',
        }).data('book', book).on('click', choose_book);
        // 创建 dropdown-img-container div
        let $dropdownImgContainer = $('<div>', {
            class: 'dropdown-img-container'
        });
        // 创建 img 元素
        let $img = $('<img>', {
            src: book['cover']
        });
        $dropdownImgContainer.append($img);
        // 创建 dropdown-text-container div
        let $dropdownTextContainer = $('<div>', {
            class: 'dropdown-text-container'
        });
        // 创建第一段文字的 div
        let $firstTextDiv = $('<div>').append(
            $('<span>').text('标题：'),
            $('<span>').text(book['title'])
        );
        // 创建第二段文字的 div
        let $secondTextDiv = $('<div>').append(
            $('<span>').text('ISBN：'),
            $('<span>').text(book['isbn'])
        );
        let $jump_to = $('<a>', {href: "/book/" + book['id'] + "/"}).append(
            $('<span>').text('跳转到书籍详情页 '),
            $('<img src="/media/icon/box-arrow-up-right.svg">')
        )
        // 将文字 div 添加到 dropdown-text-container
        $dropdownTextContainer.append($firstTextDiv, $secondTextDiv, $jump_to);
        // 将 img-container 和 text-container 添加到 item-container
        $dropdownItemContainer.append($dropdownImgContainer, $dropdownTextContainer);
        // 将 item-container 添加到页面上的某个元素（例如 id 为 dropdown-container 的 div）
        wrapper.append($dropdownItemContainer);
    }
}

function choose_book(event) {
    const book = $(event.currentTarget).data('book');
    let cover = book['cover'];
    const title = book['title'];
    const isbn = book['isbn'];
    const id = book['id'];
    let bound_book = $("#bound-book");
    if (cover === undefined)
        cover = "";
    bound_book.find("img").eq(0).attr('src', cover);
    bound_book.find("#book-other-data div").eq(0).find('span').eq(1).text(title);
    bound_book.find("#book-other-data div").eq(1).find('span').eq(1).text(isbn);
    bound_book.find("a").attr("href", "/book/" + id + "/")
    bound_book.show();
}

function cancel_bind() {
    $("#cancel-bind").on('click', function () {
        $("#bound-book").hide();
    });
}