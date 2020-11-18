
function getAvailableContainerImages(callback){
  let api_route = Flask.url_for("docker_api.get_available_container_images")
  $.get(api_route,(data)=>{
    callback(data)
  })
}

function deleteNetworkPreset(id,callback){
  let api_route = Flask.url_for("docker_api.delete_network_preset",{"id":id})
  return $.ajax({
    url: api_route,
    type: 'DELETE',
    success: callback
  });
}

function createNetworkPreset(name,containers,callback){
  let api_route = Flask.url_for("docker_api.create_network_preset")
  let payload = {
    "name":name,
    "containers":containers
  }
  postDataAsJson(api_route,payload,callback)
}

function regenVpnData(callback)
{
  let api_route = Flask.url_for("user_api.regen_auth_files")
  $.get(api_route,callback)
}


function createGroup(name,callback){
  let api_route = Flask.url_for("user_api.create_group")
  let data = {"name":name}
  postDataAsJson(api_route,data,callback)
}

function deleteGroup(id,callback){
  let api_route = Flask.url_for("user_api.delete_group",{"id":id})
  return $.ajax({
    url: api_route,
    type: 'DELETE',
    success: callback
  });
}

function redeemFlag(flag,callback){
  let api_route = Flask.url_for("docker_api.redeem_flag")
  data = {"flag":flag}
  postDataAsJson(api_route,data,callback)
}

function postDataAsJson(url,data,callback){
  $.ajax({
    url: url,
    type: "POST",
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8",
    success: (result)=>{callback(result)}
});
}
