$(document).ready(function () {
    $(".django-ckeditor-widget").css({'width': '100%'});
    $("#bound-book").hide();
    bind_book();
    cancel_bind();


    // 文章标签
    let labels_all = $("#labels-chosen");
    labels_all.on("click", "button", function () {
        $(this).parent().remove();
    });
    $("#label-add").click(function () {
        let input = $(this).prev();
        let input_val = input.val();
        if (input_val.trim().length !== 0) {
            if ($("#labels-chosen div").length >= 6) {
                show_toast("text-bg-warning", "提示", "", "标签太多啦！")
                return;
            }
            const label = $("<div class=\"border rounded-pill px-2 bg-secondary-subtle me-2 mb-2\"></div>");
            const remove = $("<button type='button'>×</button>");
            const span = $("<span></span>")
            span.text(input_val);
            label.append(span, remove);
            labels_all.append(label);
            input.val("");
        }
    });

    // 发布文章
    $("#ckeditor-submit").click(function (event) {
        event.preventDefault();
        // 标题
        let title_input = $("#editor-post-title");
        let title = title_input.val().trim();
        if (title.length < 5 || title.length > 30) {
            title_input.attr("class", "form-control is-invalid");
            title_input.next().text("应在5-50个字符之间(当前字符数" + title.length + ")")
            return;
        }
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
        $("#ckeditor-form").submit();
    })

    // 提交表单反馈
    let feedback = $("#editor-invalid-feedback").text();
    if (feedback.trim().length !== 0) {
        let hint = "";
        if (feedback.trim() === "这个字段是必填项。") {
            hint = "文章空空如也"
        }
        show_toast("text-bg-danger", "发布失败", "", hint);
    }
})

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