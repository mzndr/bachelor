$(document).ready(function(){
  placeCopyButtons()
})

class Messaging{
  static closeMessage(button){
    $(button).parent().fadeOut()
  }
  
  static createMessage(message,type=""){
    let $messages_div = $("#messages")
  
    let bg = ""
  
    switch (type) {
      case "error":
        bg = "bg-danger"
        break;
      case "warning":
        bg = "bg-warning"
        break;
      case "success":
        bg = "bg-success"
        break;
      default:
        bg = "bg-info"
        break;
    }
  
    let message_div_html = `<div class="jumbotron ${bg} elevation-1 mb-3">
    <button type="button" onclick="Messaging.closeMessage(this)" class="close" aria-label="Close">
      <span aria-hidden="true">×</span>
    </button>
    <span>${message}</span>
  </div>`
  
  let $message_div = $(message_div_html).hide()
  $messages_div.append($message_div)
  $message_div.fadeIn()
  
  }
}

function placeCopyButtons(){
  $("code").each(function(){
    let $code = $(this)

    let text = $code.text()
    $code.wrap("<span class='copy-span elevation-1'></span>")
    $code.after(`<button class="btn btn-primary btn-xs ml-2" onclick="copyToClipborad('${text}')"><i class="far fa-copy"></i></button>`)
  })
}

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