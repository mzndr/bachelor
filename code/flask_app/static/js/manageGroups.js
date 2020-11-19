class ManageGroups{
  static submitData(){

    let name = $("#group_name").val()
  
    Api.createGroup(name,()=>{
      alert("Group created")
    })
  }
  
  static deleteGroup(id){
    Api.deleteGroup(id,(data)=>{
      $(`#group_${id}`).hide()  // Dont remove it, because the changing of the dom structure breaks the 
                                // confirmation modal              
    })
  }
}
