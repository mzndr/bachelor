function getHint(networkID,flagId,button){
  Api.getHint(networkID,flagId,(data)=>{
    let $table_body = $(`#flag_${flagId}_hints`).find(`tbody`)
    console.log(data)
    if( data["status"] == "success" && data["hint"] == null){
      Messaging.createTemporalMessage("There are no hints left!","info",timeout=2900)
    }
    else if(data["status"] == "success"){
      $table_body.find('.none').remove()
      $table_body.append(`<tr><td>${data["hint"]}</tr></td>`)
      Messaging.createTemporalMessage("Hint received!","success")
    }
    else if(data["status"] == "timeout"){
      Messaging.createMessage(`Next hint at ${data["hint"]}!`,"info")
    }
  })
}

