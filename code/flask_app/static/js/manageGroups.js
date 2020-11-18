function submitData(){

  let name = $("#group_name").val()

  createGroup(name,()=>{
    alert("Group created")
  })
}

function deleteGroupButton(id){
  deleteGroup(id,(data)=>{
    console.log("deleted")
    $(`#group_${id}`).hide()  // Dont remove it, because the changing of the dom structure breaks the 
                              // confirmation modal              
  })
}