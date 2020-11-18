$(document).ready(function(){
  $("code").each(function(){
    let $code = $(this)

    let text = $code.text()
    $code.wrap("<span class='copy-span elevation-1'></span>")
    $code.after(`<button class="btn btn-primary btn-xs ml-2" onclick="copyToClipborad('${text}')"><i class="far fa-copy"></i></button>`)
  })
})

function copyToClipborad(text){
  let id = "tmp_textbox_" + Math.random();
  let $tmpTextarea = $(`<textarea id="${id}" style=""><textarea/>`)
  $(document.body).append($tmpTextarea)
  $tmpTextarea.val(text)

  var copyText = document.getElementById(id);
  copyText.select(); 

  document.execCommand("copy");
  $tmpTextarea.remove()

}