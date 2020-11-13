$(document).ready(function(){
  $("code").each(function(){
    let $code = $(this)

    let text = $code.text()
    $code.wrap("<span></span>")
    $code.after(`<button class="btn btn-primary btn-xs" onclick="copyToClipborad('${text}')"><i class="far fa-copy"></i></button>`)
  })
})

function copyToClipborad(text){
  let $tmpTextarea = $('<textarea id="abhfds3234" style="display:none;"><textarea/>')
  $(document.body).append($tmpTextarea)
  $tmpTextarea.val(text)

  var copyText = document.getElementById("abhfds3234");
  copyText.select(); 

  document.execCommand("copy");
  $tmpTextarea.remove()

}