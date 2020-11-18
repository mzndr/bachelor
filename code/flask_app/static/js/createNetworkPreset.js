function addEntries(){
  let $availableField = $("#available_images")
  let $selectedField = $("#selected_images")

  let selectedValues = $availableField.val()

   for(let val of selectedValues){
     $selectedField.append(`<option value="${val}" >${val}</option>`)
   }


}
function removeEntries(){
  let $selectedField = $("#selected_images")
  let selectedValues = $selectedField.find(":selected")
  for(let $option of selectedValues){
    $option.remove()
  }
}

function submitData(){
  let name= $("#name").val()
  let containers = []
  if (name == undefined){ return }

  $("#selected_images option").each(function()
  {
      containers.push($(this).val())
  });

  createNetworkPreset(name,containers,(data)=>{
    location.reload(); 
  })
}

function load_available_images(){
  getAvailableContainerImages((data)=>{
  let $unselectedField = $('#available_images')
  for (const [key, value] of Object.entries(data)) {
    $unselectedField.append(`<option id="${key}" value="${key}" data-toggle="tooltip" title="${value["description"]}">${key}</option>`)
  }
})
}

$(document).ready(()=>{
  load_available_images()
})