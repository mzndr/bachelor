$(document).ready(function(){
  placeCopyButtons()
  Messaging.messageFromUrlParam()
})

class Messaging{


  static messageFromUrlParam(){
    let searchParams = new URLSearchParams(window.location.search)
    if (searchParams.has('message')){
      let message = JSON.parse(searchParams.get('message'))
      let type = Object.keys(message)[0]
      let text = message[type]
      Messaging.createMessage(text,type)
    }
  }

  static closeMessage(button){
    $(button).parent().fadeOut()
  }
  
  static getMessageDiv(message,type){
    let bg = ""
  
    switch (type) {
      case "error":
        bg = "alert-danger"
        break;
      case "warning":
        bg = "alert-warning"
        break;
      case "success":
        bg = "alert-success"
        break;
      default:
        bg = "alert-info"
        break;
    }
  
    let message_div_html = 
    `<div class="alert ${bg} elevation-1 mb-3">
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
    return $message_div
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

  static createTemporalMessage(message,type="",timeout=1800){
    let $messages_div = $("#messages")
    let $message_div = Messaging.getMessageDiv(message,type)
    $messages_div.append($message_div)
    $message_div.fadeIn()
    setTimeout(()=>{
      $message_div.fadeOut()
    },timeout)
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
  Messaging.createTemporalMessage("Text Copied!","success")

}


function submitFlag(){
  let flag = $("#submit_flag_text").val()
  $("#submit_flag_text").val("")
  Api.redeemFlag(flag,(response)=>{
    console.log(response)
    let status = response.status
    let message = response.responseJSON.status
    switch (status) {
      case 404:
        Messaging.createMessage(message,"error")
        break;
      case 410:
        Messaging.createMessage(message,"warning")
          break;
      case 1337:
        Messaging.createMessage(message,"success")
        break;
    }

  })
}