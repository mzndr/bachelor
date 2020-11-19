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
    Api.deleteNetworkPreset(id,(data)=>{
      console.log("deleted")
      $(`#${id}`).hide() // Dont remove it, because the changing of the dom structure breaks the 
                         // confirmation modal              
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

  static startNetwork(id){
    let loading_icon = "<div class='spinner-border mr-2' role='status'></div>"
    let $name = $(`#${id}_network_name`)
    let $usersField = $(`#${id}_assign_users`)
    let $groupsField = $(`#${id}_assign_groups`)

    let name = $name.val()
    let userIds = $usersField.val()
    let groupIds = $groupsField.val()


    Api.startNetworkFromPreset(
      id,
      name,
      groupIds,
      userIds,
      (data)=>{
        location.reload();
      }
    )
    
    $(`#${id}_icon`).replaceWith(loading_icon)


  }
}








$(document).ready(()=>{
  CreatePreset.loadAvailableImages()
  StartNetwork.loadGroupsAndUsers()
})