function clear() {
    document.body.innerHTML = '';
}
//把html内容添加到列表最后
function __appContentHtml(html) {
    var content = document.getElementById('chatContent');
    content.insertAdjacentHTML("beforeend", html);
}
//获取对方内容的html
//获取我发内容的html
//添加文本内容
function appendText(headImg, text, tx) {
    var headImgClass = tx ? 'divMyHead' : 'divotherHead';
    var textClass = tx ? 'triangle-right right' : 'triangle-left left';
    var headImgWidth = '50px';
    var headImgHeight = '50px';
    var html = "\n            <div style='overflow:hidden;'>\n                <img src='" + headImg + "' class='" + headImgClass + "' width='" + headImgWidth + "' height='" + headImgHeight + "'/>\n                <p class='" + textClass + "'>" + text + "</p>\n            </div>\n        ";
    __appContentHtml(html);
}
//添加提示内容
function appNotice(text) {
    var html = "\n            <div class=\"chat-notice\">\n                <span>" + text + "</span>\n            </div>\n        ";
    __appContentHtml(html);
}
