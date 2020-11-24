$(document).ready(function(){
  placeCopyButtons()
})

class Messaging{
  static closeMessage(button){
    $(button).parent().fadeOut()
  }
  
  static getMessageDiv(message,type){
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
  
    let message_div_html = 
    `<div class="jumbotron ${bg} elevation-1 mb-3">
      <button type="button" onclick="Messaging.closeMessage(this)" class="close" aria-label="Close">
        <span aria-hidden="true">×</span>
      </button>
      <span>${message}</span>
    </div>`
  
    let $message_div = $(message_div_html).hide()
    return $message_div
  }
  static createMessage(message,type=""){
    let $messages_div = $("#messages")
    let $message_div = Messaging.getMessageDiv(message,type)
    $messages_div.append($message_div)
    $message_div.fadeIn()
  }

  static apiResponseToMessage(response){
    let status = response.status
    let messageType = ""
    let message = response.responseText
    switch (status) {
      case 200:
        messageType = "success"
      default:
        messageType = "error"
        break;
    }
    Messaging.createMessage(message,messageType)
  }

  static createTemporalMessage(message,type=""){

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


function submitFlag(){
  let flag = $("#submit_flag_text").val()
  $("#submit_flag_text").val("")
  Api.redeemFlag(flag,(response)=>{
    let message = response.responseJSON["status"]
    let status = response.status 

    switch (status) {
      case 404:
        Messaging.createMessage(message,"error")
        break;
      case 410:
        Messaging.createMessage(message,"warning")
          break;
      case 200:
        Messaging.createMessage(message,"success")
        break;
    }

  })
}