let loading_icon = "<div class='spinner-border mr-2' role='status'></div>"
class CreatePreset{
  static addEntries(){
    let $availableField = $("#available_images")
    let $selectedField = $("#selected_images")
  
    let selectedValues = $availableField.val()
  
     for(let val of selectedValues){
       $selectedField.append(`<option value="${val}" >${val}</option>`)
     }
  }

  static removeEntries(){
    let $selectedField = $("#selected_images")
    let selectedValues = $selectedField.find(":selected")
    for(let $option of selectedValues){
      $option.remove()
    }
  }
  
  static submitData(){
    let name= $("#create_preset_name").val()
    let containers = []
    if (name == undefined){ return }
  
    $("#selected_images option").each(function()
    {
        containers.push($(this).val())
    });

    Api.createNetworkPreset(name,containers,(data)=>{
      location.reload(); 
    })
  }
  
  static loadAvailableImages(){
    Api.getAvailableContainerImages((data)=>{
    let $unselectedField = $('#available_images')
    for (const [key, value] of Object.entries(data)) {
      $unselectedField.append(`<option id="${key}" value="${key}" data-toggle="tooltip" title="${value["description"]}">${key}</option>`)
      }
    })
  }
}

class ManagePreset{
  static deleteNetworkPreset(id){
    Api.deleteNetworkPreset(id,(response)=>{
      console.log("deleted")
      $(`#${id}`).hide() // Dont remove it, because the changing of the dom structure breaks the 
                         // confirmation modal   
      Messaging.createMessage("Preset deleted!","success")           
    })
  }
}

class StartNetwork{
  static loadGroupsAndUsers(){
    Api.getAllUsers((userData)=>{
      Api.getAllGroups((groupData)=>{
        let $userFields = $(".assign_users")
        let $groupFields = $(".assign_groups")

        $groupFields.each(function(){
          for(let group of groupData){
            let id = group["id"]
            let name = group["name"]
            $(this).append(`<option id="group_${id}" value="${id}">${name}</option>`)
          }
        })

        $userFields.each(function(){
          for(let user of userData){
            let id = user["id"]
            let username = user["username"]
            $(this).append(`<option id="user_${id}" value="${id}">${username}</option>`)
          }
        })

      })
    })

  }

  static startNetwork(id,button){
    
    let $button = $(button)
    let $name = $(`#${id}_network_name`)
    let $usersField = $(`#${id}_assign_users`)
    let $groupsField = $(`#${id}_assign_groups`)

    let $createMultipleField = $(`#${id}_create_for_everyone`)
    let name = $name.val()
    let userIds = $usersField.val()
    let groupIds = $groupsField.val()
    let original_icon = $button.html();
    if($createMultipleField.prop('checked')){
      console.log("CREATING MULTIPLE")
      Api.startMultipleNetworksFromPreset(
        id,
        name,
        groupIds,
        userIds,
        (response,error)=>{
          $("#modalstart_" + id).modal('hide')
          $button.html(original_icon)
          if (error){
            if (response.status == 0){
              Messaging.createMessage("Networks created!","success")
            } 
            else
            {
              Messaging.apiResponseToMessage(response)
            }
          }else{
            Messaging.createMessage("Networks created!","success")
          }
          NetworkRendering.fetchNetworks()
        }
      )
    }
    else
    {
      Api.startNetworkFromPreset(
        id,
        name,
        groupIds,
        userIds,
        (response,error)=>{
          $("#modalstart_" + id).modal('hide')
          $button.html(original_icon)
          if (error){
            if (response.status == 0){
              Messaging.createMessage("Network created!","success")
            } 
            else
            {
              Messaging.apiResponseToMessage(response)
            }
          }else{
            Messaging.createMessage("Network created!","success")
          }
          NetworkRendering.fetchNetworks()
        }
      )
    }
    
    $button.html(loading_icon)

    
    
    


  }
}

class ManageNetwork{
  static deleteNetwork(id,button){
    let $button = $(button)
    let original_icon = $button.html();
    $button.html(loading_icon)
    Api.deleteNetwork(id,(response)=>{
      

      NetworkRendering.removeNetwork("network_" + id)
      Messaging.createMessage("Deleted network","success")
      $button.html(original_icon)
    })
  }

  static restartNetwork(id,button){
    let $button = $(button)
    let original_icon = $button.html();

    $button.html(loading_icon)
    Api.restartNetwork(id,(response)=>{
      NetworkRendering.fetchNetworks()
      $button.html(original_icon)
      Messaging.createMessage("Restarting network...","success")
    })
  }
}


class NetworkRendering{
  
  static fetchNetworks()
  {
    let $table = $("#running_networks_rows")

    Api.getAllNetworks((data)=>{
      for (let network of data){
        let found = false
        $table.children("tr").each(function(i){
          let rowId = $(this).attr("id")
          if(rowId == `network_${network.id}`)
          {

            NetworkRendering.replaceNetwork(rowId,network)
            found = true
          }

        })
        if(!found){
          NetworkRendering.appendNetwork(network)
        }
      }

    })
  }

  static clearTable(){
    $("#running_networks_rows").html("")
  }

  static replaceNetwork(row_id,network_json){
    let $row = $(`#${row_id}`)
    let array = NetworkRendering.getNetworkRowArray(network_json)
    networktable.row(`#${row_id}`).data(array).draw()
  }

  static removeNetwork(row_id){
    networktable.row(`#${row_id}`).remove().draw()
  }

  static appendNetwork(network_json){
    
    let row_html = NetworkRendering.getNetworkRowHtml(network_json)
    networktable.row.add($(row_html)).draw().node();
  }

  static getStatusBadge(status){
    
    let color;
    let tooltip;

    switch (status) {
      case "running":
        color = "bg-success"
        tooltip = "Network is running!"
        break;
      case "starting":
        color = "bg-warning"
        tooltip = "Network is starting..."
        break;
      case "error":
        color = "bg-danger"
        tooltip = "Something went wrong while starting the network :("
        break;
      default:
        color = "bg-info"
        tooltip = "unknown network state"
        break;
    }

    let badge = `
    <span class="badge badge-pill ${color}" data-toggle="tooltip" data-placement="right" title="${tooltip}">
    ${status}
    </span>
    `
    return badge
  }
  
  static getNetworkRowArray(network_json)
  {
    let id = network_json.id;
    let status = network_json.status;
    let name = network_json.clean_name;
    let presetName = network_json.preset;
    let command = network_json.command;
    let details_url =  Flask.url_for("networks.network_details",{"id":id});
    
    
    let array = [
      `${NetworkRendering.getStatusBadge(status)}`,
      `${name}`,
      `${presetName}`,
      `<span class="copy-span elevation-1"><code>${command}</code><button class="btn btn-primary btn-xs ml-2" onclick="copyToClipborad('${command}')"><i class="far fa-copy"></i></button></span>`,
      `<button class="btn btn-danger control-button" onclick="ManageNetwork.deleteNetwork('${id}', this)"><i class="fas fa-trash-alt"></i></button>
      <button class="btn btn-warning control-button" onclick="ManageNetwork.restartNetwork('${id}', this)"><i class="fas fa-redo-alt"></i></button>
      <button class="btn btn-primary" onclick="window.location=\`${details_url}\`">
        <i class="fas fa-info-circle mr-1"></i>
        Details
      </button>`
    ] 
    
    
    return array
  
  }

  static getNetworkRowHtml(network_json)
  {
    console.log(network_json)
    let id = network_json.id;
    let status = network_json.status;
    let name = network_json.clean_name;
    let presetName = network_json.preset;
    let command = network_json.command;
    let details_url =  Flask.url_for("networks.network_details",{"id":id});
    
    
    let table_row = `
    <tr id="network_${id}" role="row">
    <td>
      ${NetworkRendering.getStatusBadge(status)}
  
    </td>
      <td>${name}</td>
      <td>${presetName}</td>
      <td><span class="copy-span elevation-1"><code>${command}</code><button class="btn btn-primary btn-xs ml-2" onclick="copyToClipborad('${command}')"><i class="far fa-copy"></i></button></span></td>
      <td>
        <button class="btn btn-danger control-button" onclick="ManageNetwork.deleteNetwork('${id}', this)"><i class="fas fa-trash-alt"></i></button>
        <button class="btn btn-warning control-button" onclick="ManageNetwork.restartNetwork('${id}', this)"><i class="fas fa-redo-alt"></i></button>
        <button class="btn btn-primary" onclick="window.location=\`${details_url}\`">
          <i class="fas fa-info-circle mr-1"></i>
          Details
        </button>
      </td>
    </tr>
  `
    return table_row
  
  }
}



let networktable;

$(document).ready(()=>{
  CreatePreset.loadAvailableImages()
  StartNetwork.loadGroupsAndUsers()
  NetworkRendering.fetchNetworks()

  window.setInterval(()=>{NetworkRendering.fetchNetworks()}, 1000);

  networktable = $("#networktable").DataTable()
  $("#presettable").DataTable()
})
