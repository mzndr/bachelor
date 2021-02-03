function regenVpnDataButton(){
  loading_icon = "<div id='regen_data_button_icon' class='spinner-border' role='status'></div>"
  done_icon = "<i id='regen_data_button_icon' class='fas fa-check-circle mr-1'></i>"
  $icon = $("#regen_data_button_icon")
  $icon.replaceWith(loading_icon)
  $icon = $("#regen_data_button_icon")
  Api.regenVpnData((data)=>{
    $icon.replaceWith(done_icon)
  })

}