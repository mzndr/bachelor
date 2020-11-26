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
    let name = $name.val()
    let userIds = $usersField.val()
    let groupIds = $groupsField.val()
    let original_icon = $button.html();
    
    
    $button.html(loading_icon)

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
      }
    )
    
    


  }
}

class ManageNetwork{
  static deleteNetwork(id,button){
    let $button = $(button)
    let original_icon = $button.html();
    let $tr = $("#network_" + id)
    $button.html(loading_icon)
    Api.deleteNetwork(id,(response)=>{
      $button.html(original_icon)
      $tr.hide()

      Messaging.createMessage("Deleted network","success")
    })
  }

  static restartNetwork(id,button){
    let $button = $(button)
    let original_icon = $button.html();

    $button.html(loading_icon)
    Api.restartNetwork(id,(response)=>{
      $button.html(original_icon)
      Messaging.createMessage("Restarted network","success")
    })
  }
}







$(document).ready(()=>{
  CreatePreset.loadAvailableImages()
  StartNetwork.loadGroupsAndUsers()
})