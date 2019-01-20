const preview_box_id = 'preview_box';

const md = window.markdownit();
const preview_box = document.getElementById('preview_box');

/** Form input */
const inp_title = document.querySelector('#editor #page_title');
const inp_textarea = document.getElementById('rev_body');

/** Preview */
const prv_title = document.querySelector(`#${preview_box_id} #page #title`);
const prv_timestamp = document.querySelector(`#${preview_box_id} #page #timestamp`);
const prv_content = document.querySelector(`#${preview_box_id} #page #content`);


/** Update preview with current input */
var update_preview = function() {
    prv_title.innerHTML = md.render(inp_title.value);
    prv_timestamp.innerHTML = new Date();
    prv_content.innerHTML = md.render(inp_textarea.value.trim());
}

/** update and shows preview_box */
var show_preview = function(e) {
    update_preview();
    preview_box.hidden = false;
}

/** hide preview_box */
var close_preview = function(e) {
    preview_box.hidden = true;
}

/** Keyboard shortcuts */
let timeout = 0;
document.querySelector('body').addEventListener('keyup',
    function(e) {
        if(e.key == 'Escape' || e.code == 'Escape') {
            // Close preview 'ESC'
            e.preventDefault();
            close_preview();
        } else if(e.key == 'Shift') {
            // Show preview 'Shift x2'
            if (timeout) {
                e.preventDefault();
                timeout = 0;
                show_preview();
            } else {
                timeout = 1;
                setTimeout(() => {timeout = 0}, 1500);
            }
        }
    }
);


