
function submitFlag(){
  flag = $("#submit_flag_text").val()
  Api.redeemFlag(flag,(data)=>{
    console.log(data)
  })
}