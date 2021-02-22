function loadFlags()
{
  Api.getFlags(networkId,(data)=>{
    for(let flag of data)
    {
      if (!flag.redeemed){
        let card = $(getUnredeemedFlagCard(flag))
        $("#tasks").append(card)
      }
    }
    for(let flag of data)
    {
      if (flag.redeemed){
        let card = $(getRedeemedFlagCard(flag))
        $("#tasks").append(card)
      }
    }
  })
}

function removeFlagCards(){
  $("#tasks").empty()
}

function getUnredeemedFlagCard(flagJson)
{
    let revealedHints = flagJson.revealed_hints
    let hints = ""
    if(revealedHints.length <= 0){
      hints = `<tr class="none" ><td>None.</td></tr>`
    }else{
      for(let hint of revealedHints)
      {
        hints = hints + `<tr><td>${hint}</td></tr>`
      }
    }
    let card = `<div class="card card-secondary card-outline bg-dark elevation-3 p-2 card-danger">
    <div class="card-header">
      <div class="card-title"><h4>${flagJson.description}</h4></div>
      <div class="card-tools">
        <button type="button" class="btn btn-tool" data-card-widget="collapse" data-toggle="tooltip" title="Collapse">
          <i class="fas fa-minus"></i></button>
        <button type="button" class="btn btn-tool" data-card-widget="remove" data-toggle="tooltip" title="Remove">
          <i class="fas fa-times"></i></button>
      </div>
    </div>
    <div class="card-body">
      <table id="flag_${flagJson.id}_hints" class="table table-dark elevation-2 mb-3">
        <thead>
          <tr>
            <th>Hints</th>
          </tr>
        </thead>
        <tbody>
          ${hints}
        </tbody></table>

      <button class="btn btn-primary" onload="buttonTimer(${flagJson.id},this)" onclick="getHint(${networkId},${flagJson.id})">
        Get a Hint!
      </button>
    </div>
    <!-- /.card-body -->
  </div>`
  return card
}

function adjustNetworkCompletion()
{
  Api.getNetwork(networkId,(response)=>{
    let $pbar = $("#network_progress")
    $pbar.css("width",response.completion+"%")
    $('#network_completion').text(`${response.redeemed_flags} of ${response.total_flags} flags redeemed!`)
    
  })

}

function getRedeemedFlagCard(flagJson)
{

    let revealedHints = flagJson.revealed_hints
    let hints = ""
    if(revealedHints.length <= 0){
      hints = `<tr><td>None.</td></tr>`
    }else{
      for(let hint of revealedHints)
      {
        hints = hints + `<tr><td>${hint}</td></tr>`
      }
    }

    let card = `<div class="card card-secondary card-outline bg-dark elevation-3 p-2 card-success">
    <div class="card-header">
      <div class="card-title"><h4>${flagJson.description}</h4></div>
      <div class="card-tools">
        <button type="button" class="btn btn-tool" data-card-widget="collapse" data-toggle="tooltip" title="Collapse">
          <i class="fas fa-minus"></i></button>
        <button type="button" class="btn btn-tool" data-card-widget="remove" data-toggle="tooltip" title="Remove">
          <i class="fas fa-times"></i></button>
      </div>
    </div>
    <div class="card-body">
      <table id="flag_${flagJson.id}_hints" class="table table-dark elevation-2 mb-3">
        <thead>
          <tr>
            <th>Hints</th>
          </tr>
        </thead>
        <tbody>
          ${hints}
        </tbody></table>
    </div>
    <!-- /.card-body -->
  </div>`
  return card
}

function getHint(networkID,flagId){
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

function overwriteSubmitFlag(){
  submitFlag = ()=>{
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
          removeFlagCards()
          loadFlags()
          adjustNetworkCompletion()
          adjustUserCompletion()
          break;
      }
    })
  }
}

$(document).ready(()=>{
  loadFlags()
  overwriteSubmitFlag()

})