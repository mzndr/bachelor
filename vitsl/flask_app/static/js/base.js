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
    let message = response.responseText
    let messageType = ""
    if (status == undefined){
      messageType = "success"
      message = response
    }
    else
    {
      messageType = "error"
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
    $code.after(`<button class="btn btn-primary btn-xs ml-2" onclick="copyToClipborad('${text}',this)"><i class="far fa-copy"></i></button>`)
  })
}

function copyToClipborad(text,element){
  // Create a random id for the textarea
  let id = "tmp_textbox_" + Math.random();
  // Create a temporal textarea, with the text to copy inside it
  let $tmpTextarea = $(`<textarea id="${id}" style="">${text}</textarea>`)
  // If a element was given append the textarea to 
  // the element, if not append it to the body.
  // For focus problems on modals
  if(element){ $(element).append($tmpTextarea) }
  else{ $(document.body).append($tmpTextarea) }

  // Get the temporal textarea
  let copyText = document.getElementById(id);
  // Select the text inside the textarea
  copyText.select();
  // Execute the copy command
  document.execCommand("copy");
  // Remove the temporal textarea
  $tmpTextarea.remove()
  // Tell the user that the text was copied.
  Messaging.createTemporalMessage("Text copied to clipboard!","success")
}


function submitFlag(){
  let flag = $("#submit_flag_text").val()
  $("#submit_flag_text").val("")
  Api.redeemFlag(flag,(response)=>{
    console.log(response)
    let status = response.status
    switch (status) {
      case 404:
        Messaging.createMessage("Invalid flag!","error")
        break;
      case 410:
        Messaging.createMessage("Flag was already redeemed!","warning")
          break;
      case 1337:
        Messaging.createMessage("Flag successfully redeemed!","success")
        break;
    }

  })
}