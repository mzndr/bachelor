function deleteNetworkPresetButton(id){
  deleteNetworkPreset(id,(data)=>{
    console.log("deleted")
    $(`#${id}`).hide() // Dont remove it, because the changing of the dom structure breaks the 
                       // confirmation modal              
  })
}