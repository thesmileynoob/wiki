const md = window.markdownit()
let content = document.getElementById('content')
content.innerHTML = md.render(content.innerHTML)
