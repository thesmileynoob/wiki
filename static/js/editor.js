
const md = window.markdownit();
const preview = document.getElementById('preview');
const textarea = document.getElementById('rev_body');
console.log('hello');

var show_preview = function(e) {
    preview.innerHTML = md.render(textarea.value.trim());
    preview.hidden = false;
}

var close_preview = function(e) {
    preview.hidden = true;
}


