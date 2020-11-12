
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
    name,
    containers
  }
  postDataAsJson(api_route,payload,callback)
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

