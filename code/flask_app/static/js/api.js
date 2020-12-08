class Api{

  static getAvailableContainerImages(callback){
    let api_route = Flask.url_for("docker_api.get_available_container_images")
    $.get(api_route,(data)=>{
      callback(data)
    })
  }
  
  static startNetworkFromPreset(presetId,name,groupIds,userIds,callback){
    let api_route = Flask.url_for("docker_api.start_network",{"id":presetId})
    let data = {
      "network_name":name,
      "assign_users":userIds,
      "assign_groups":groupIds
    }
    Api.postDataAsJson(api_route,data,callback)
  }

  static restartNetwork(id,callback){
    let api_route = Flask.url_for("docker_api.restart_network",{"id":id})
    $.get(api_route,(data)=>{
      callback(data)
    })
  }

  static getNetwork(id,callback){
    let api_route = Flask.url_for("docker_api.get_network_by_id",{"id":id})
    $.get(api_route,(data)=>{
      callback(data)
    })
  }

  static deleteNetwork(id,callback){
    let api_route = Flask.url_for("docker_api.delete_network",{"id":id})
    return $.ajax({
      url: api_route,
      type: 'DELETE',
      success: callback
    });
  }

  static deleteUser(id,callback){
    let api_route = Flask.url_for("user_api.delete_user",{"id":id})
    return $.ajax({
      url: api_route,
      type: 'DELETE',
      success: callback
    });
  }

  static deleteNetworkPreset(id,callback){
    let api_route = Flask.url_for("docker_api.delete_network_preset",{"id":id})
    return $.ajax({
      url: api_route,
      type: 'DELETE',
      success: callback
    });
  }
  
  static createNetworkPreset(name,containers,callback){
    let api_route = Flask.url_for("docker_api.create_network_preset")
    let payload = {
      "name":name,
      "containers":containers
    }
    Api.postDataAsJson(api_route,payload,callback)
  }
  
  static regenVpnData(callback)
  {
    let api_route = Flask.url_for("user_api.regen_auth_files")
    $.get(api_route,callback)
  }
  
  static createGroup(name,callback){
    let api_route = Flask.url_for("user_api.create_group")
    let data = {"name":name}
    Api.postDataAsJson(api_route,data,callback)
  }
  
  static deleteGroup(id,callback){
    let api_route = Flask.url_for("user_api.delete_group",{"id":id})
    return $.ajax({
      url: api_route,
      type: 'DELETE',
      success: callback
    });
  }
  
  static getFlagInfo(flagId,callback){
    let api_route = Flask.url_for("docker_api.get_flag_info",{"flag_id":flagId})
    $.get(api_route,(data)=>{callback(data)})
  }

  static getHint(networkId,flagId,callback){
    let api_route = Flask.url_for("docker_api.get_hint",{"flag_id":flagId, "network_id":networkId})
    $.get(api_route,(data)=>{callback(data)})
  }

  static grantRole(userId,roleName,callback){
    let api_route = Flask.url_for("user_api.grant_role",{"role_name":roleName,"user_id":userId})
    Api.putDataAsJson(api_route,{},(response)=>{
      callback(response)
    })
  }

  static revokeRole(userId,roleName,callback){
    let api_route = Flask.url_for("user_api.revoke_role",{"role_name":roleName,"user_id":userId})
    Api.putDataAsJson(api_route,{},(response)=>{
      callback(response)
    })
  }

  static redeemFlag(flag,callback){
    let api_route = Flask.url_for("docker_api.redeem_flag")
    let data = {"flag":flag}
    Api.postDataAsJson(api_route,data,callback)
  }
  
  static getAllUsers(callback){
    let api_route = Flask.url_for("user_api.get_all_users")
    $.get(api_route,(data)=>{
      callback(data)
    })
  }

  static getAllGroups(callback){
    let api_route = Flask.url_for("user_api.get_all_groups")
    $.get(api_route,(data)=>{
      callback(data)
    })
  }

  // Utils
  static postDataAsJson(url,data,callback){
    $.ajax({
      timeout:0,
      async:true,
      url: url,
      type: "POST",
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      success: (response)=>{
        callback(response,false)
      },
      error: (response)=>{

        callback(response,true)
      }
  });
  }  static putDataAsJson(url,data,callback){
    $.ajax({
      timeout:0,
      async:true,
      url: url,
      type: "PUT",
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      success: (response)=>{
        callback(response,false)
      },
      error: (response)=>{

        callback(response,true)
      }
  });
  }
}



