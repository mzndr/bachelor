class ManageGroups{
  static submitData(){

    let name = $("#group_name").val()
  
    Api.createGroup(name,(response)=>{
      location.reload()
    })
  }
  
  static deleteGroup(id){
    Api.deleteGroup(id,(data)=>{
      $(`#group_${id}`).hide()  // Dont remove it, because the changing of the dom structure breaks the 
                                // confirmation modal 
      Messaging.createMessage("Group deleted!","success")
    })
  }
}

class ManageUsers{
  static deleteUser(userId)
  {
    Api.deleteUser(userId,(response)=>{
      $(`#user_${userId}`).fadeOut()
      Messaging.createMessage("User deleted!","success")
    })
  }
  static grantRole(userId,roleName){
    Api.grantRole(userId,roleName,(response)=>{
      location.reload()
    })
  }
  static revokeRole(userId,roleName){
    Api.revokeRole(userId,roleName,(response)=>{
      location.reload()
    })
  }

  static resetPassword(userId){
    Api.resetPassword(userId,(response)=>{
      let password = response.new_password;
      let username = response.username;
      Messaging.createMessage(`${username}'s new password is ${password}`,"success")
    })
  }

}

$(document).ready(function(){
  $("#usertable").DataTable()
  $("#grouptable").DataTable()
})