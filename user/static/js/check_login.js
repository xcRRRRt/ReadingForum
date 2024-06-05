function checkUserLogin() {
    return $.get('/user/is_login/')
        .then(function (data) {
            // 在这里处理从服务器返回的数据
            return data['is_login'];
        })
        .fail(function (error) {
            console.error('There was a problem with the fetch operation:', error);
            return false; // 出现错误时返回 false
        });
}
