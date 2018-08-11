function clear() {
    document.body.innerHTML = ''
}
//把html内容添加到列表最后
function __appContentHtml(html:string){
    let content = document.getElementById('chatContent');
    content.insertAdjacentHTML("beforeend", html);
}
//获取对方内容的html
//获取我发内容的html
//添加文本内容
function appendText(headImg:string, text:string,tx:boolean){
    let headImgClass = tx ? 'divMyHead' : 'divotherHead';
    let textClass = tx ? 'triangle-right right':'triangle-left left';
    const headImgWidth = '50px';
    const headImgHeight = '50px';

    let html =
        `
            <div style='overflow:hidden;'>
                <img src='${headImg}' class='${headImgClass}' width='${headImgWidth}' height='${headImgHeight}'/>
                <p class='${textClass}'>${text}</p>
            </div>
        `;
    __appContentHtml(html);
}

//添加提示内容
function appNotice(text:string){
    let html =
        `
            <div class="chat-notice">
                <span>${text}</span>
            </div>
        `;
    __appContentHtml(html);
}