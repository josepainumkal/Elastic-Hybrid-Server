
var fetchModelRunsURL;
var pushed_model_info;

$(document).ready(function () {
  //your code here
  get_seams_tasks_info();
  get_seams_info();

});

// setInterval(get_seams_tasks_info,100);
// setInterval(get_seams_info,100);

function get_seams_tasks_info(){
   $.ajax({
      type: "GET",
      url: '/get_seams_tasks',
      // contentType: "application/json; charset=utf-8",
      dataType: 'json',
      contentType: 'application/json',
      success: function(data) {
          // var jsonData = JSON.parse(data); 
          list_seams_tasks(data);
      }
    });

}

function get_seams_info(){
   $.ajax({
      type: "GET",
      url: '/get_seams_info',
      contentType: "application/json; charset=utf-8",
      dataType: 'json',
      contentType: 'application/json',
      success: function(data) {
          // var jsonData = JSON.parse(data); 
          list_seams_info(data);
      }
    });

}

function list_seams_info(data){
  $('#budget_amount').text(data.budget_amount);
  $('#amount_remaining').text(data.amount_remaining);
  $('#models_owned').text(data.models_owned);
  $('#models_rented').text(data.models_rented);
  $('#total_models').text(data.total_models);

  // for Update Page

  $('#u_available').text(data.amount_remaining);
  $('#u_period').text(data.budget_period);
  $('#u_interval').text(data.time_interval);
  $('#u_maxrentedtotal').text(data.total_rented_modelruns_allowed);
  $('#u_lambda').text(data.lamda);
  $('#u_instance_cost').text(data.instance_cost);
  // $('#u_qlength').text(data.total_models);
  // $('#u_waittime').text(data.total_models);


}



function list_seams_tasks(data){
  $('#seams-task-items').text('');

  for(var i = 0; i<data.length; i++){
     $('#seams-task-items').append("<tr key="+data[i].modelId.toString()+">" +
                                     "<td>"+data[i].modelId+"</td>" +
                                     "<td>"+data[i].waittime+"</td>" +
                                     "<td>"+data[i].runtime+"</td>" +
                                     "<td>"+data[i].workername+"</td>" +
                                     "<td>"+data[i].workertype+"</td>" +
                                     "<td>"+data[i].amount_for_task+"</td>" +
                                     "<td>"+data[i].taskId+"</td>" +
                                      // the button id is modelrunID
                                      // "<td><button class='modelRunChosenButton' id='"+tempItem.id.toString()+"' >Choose Me</button>"+"</td>" +
                                      // "<td><button class='modelRunChosenButton' id='"+buttonId+"' >"+buttonTxt+"</button>"+"</td>" +
                                   "</tr>");
  }
}


$(document).on("click", "#resetBtnId" , function() {
  $.ajax({
          type: "POST",
          url: "/resetTasks",
          // data: $('.gstoreCred').serialize(),
          success: function(response){
          },
          error: function(error) {
          }
  });
});



$(document).on("click", "#updateBtnId" , function() {

  $.ajax({
          type: "POST",
          url: "/seams_update_info",
          data: $('#update_seams').serialize(),

          success: function(response){
            var response = JSON.parse(response);
          
            $('#u_available').text(response.total_budget_amount);
            $('#u_period').text(response.total_budget_period);
            $('#u_interval').text(parseFloat(response.time_interval).toFixed(2));
            $('#u_maxrentedtotal').text(response.total_rented_modelruns_allowed);
            $('#u_lambda').text(response.lamda);
            $('#u_instance_cost').text(response.instance_cost);
            $('#update_notif').show();

          },
          error: function(error) {
          }
  });
});


function listModelRunID(data)
  {
    var vwpModelId='',pushedAt='', buttonTxt, buttonId;
    itemCount = data.num_results;
    if(itemCount != 0)
    {
      for(var i=0; i<itemCount; i++)
      {
          var tempItem = data.objects[i];
          if(tempItem.progress_state =="FINISHED"){
                    buttonTxt = "Push-VWP"
                    buttonId = tempItem.id.toString().concat('|')
                    vwpModelId='';
                    pushedAt='';

                    if(pushed_model_info[tempItem.id]){
                       buttonTxt = "Remove-VWP"
                       vwpModelId = pushed_model_info[tempItem.id][0]
                       pushedAt = pushed_model_info[tempItem.id][1]
                       buttonId = buttonId.concat(vwpModelId)
                    }
                    
                    label_vwpID = "vwpID-".concat(tempItem.id.toString())
                    label_pushID = "pushID-".concat(tempItem.id.toString())

                    $('#model-run-items').append("<tr key="+tempItem.id.toString()+">" +
                                     "<td>"+tempItem.id.toString()+"</td>" +
                                     "<td>"+tempItem.title+"</td>" +
                                     "<td>"+tempItem.created_at+"</td>" +
                                     "<td id='"+label_vwpID+"'>"+vwpModelId+"</td>" +
                                     "<td id='"+label_pushID+"'>"+pushedAt+"</td>" +
                                     // the button id is modelrunID
                                    // "<td><button class='modelRunChosenButton' id='"+tempItem.id.toString()+"' >Choose Me</button>"+"</td>" +
                                     "<td><button class='modelRunChosenButton' id='"+buttonId+"' >"+buttonTxt+"</button>"+"</td>" +
                                   "</tr>");
                    buttonSelector = '#'+buttonId
                    var btnElt = document.getElementById(buttonId);
                   
                    if(buttonTxt == "Push-VWP"){
                          btnElt.classList.remove("btn-danger");
                          btnElt.classList.add("btn-success");
                    //    $('.modelRunChosenButton').removeClass('.btn-danger').addClass('btn-success');
                    }else{
                          btnElt.classList.remove("btn-success");
                          btnElt.classList.add("btn-danger");
                          
                       //$('.modelRunChosenButton').removeClass('.btn-success').addClass('btn-danger');
                     }
          }
        }
      $('#additional-info').text('');
    }
    // there are no model runs in the model runserver
    else
    {
      $('.modelRunList').hide();
      $('#additional-info').append("<p>You do not have a modelrun in the server</p>");
    }

    // if gstore Credentials are not in session
    var gunameInSession = $('#gstore-uname').val();
    if(gunameInSession==''){
      // $('.modelRunChosenButton').hide();
      $('.modelRunChosenButton').prop('disabled', true);
      $('#gstoreCredAlert').text(' To Push/Remove models, Please save Gstore Credentials. ');

     }

  }


 $(document).on("click", "#gstoreSbtId" , function() {


  var btnText =  $('#gstoreSbtId').text();
  if(btnText=="Save"){

        var uname = $('#gstore-uname').text();
        var pwd = $('#gstore-pwd').text();
        $.ajax({
                  type: "POST",
                  url: "/setGstoreCred",
                  data: $('.gstoreCred').serialize(),
                  success: function(response){
                    var response = JSON.parse(response);
                    if(response.status=="Failed"){
                         $('#error-gstoreCred').text('*Unauthorized Credentials.');
                          $('.modelRunChosenButton').prop('disabled', true);
                          $('#gstoreCredAlert').text(' To Push/Remove models, Please save Gstore Credentials. ');
                    } else{
                          $('#error-gstoreCred').text('');

                         $('#gstoreSbtId').text('Change');
                         $('#gstore-uname').prop('disabled', true);
                         $('#gstore-pwd').prop('disabled', true);

                         $('.modelRunChosenButton').prop('disabled', false);
                         $('#gstoreCredAlert').text('');
                    }
                    //console.log(response.status);
                  },
                  error: function(error) {
                      console.log(error);
                  }
        });

  }else if(btnText=="Change"){
        $('#gstore-uname').prop('disabled', false);
        $('#gstore-pwd').prop('disabled', false);
        $('#gstoreSbtId').text('Save');

        $('#gstoreCredAlert').text(' To Push/Remove models, Please save Gstore Credentials. ');
        $('.modelRunChosenButton').prop('disabled', true);
        // $('.modelRunChosenButton').addClass('disabled');



  }
   
 });


 $(document).on("click", ".modelRunChosenButton" , function() {
      // get the current button id
      //var modelRunID = $(this).attr('id');

      $('.modelRunChosenButton').prop('disabled', true);


      var buttonId = $(this).attr('id');
      var modelRunID = buttonId.split('|')[0]
      var vwpModelId = buttonId.split('|')[1]
      var buttonTxt = $(this).text();
      var modelRunURL = fetchModelRunsURL + '/' + modelRunID;

      


      if(buttonTxt == "Remove-VWP"){
          $(this).removeClass('btn-danger').addClass('btn-info');
          $(this).text('Removing...')
          remove_vwp_push(modelRunID,vwpModelId, this)


       }else{
           $(this).removeClass('btn-success').addClass('btn-info');
          $(this).text('Pushing...')
           // get the model run information
          button =this;
          $.ajax({
            type: "GET",
            url: modelRunURL,
            contentType: "application/json; charset=utf-8",
            beforeSend : function(xhr) {
              // set header
              xhr.setRequestHeader("Authorization", "JWT " + access_token);
            },
            error : function() {
              // error handler
              console.log('get model run information failed');
            },
            success: function(data) {
                // success handler
                importChosenModelRun(data, button);
            }
          });
      }

      $('.modelRunChosenButton').prop('disabled', false);

       
  });


function importChosenModelRun(data, button){
    var controlURL, dataURL, paramURL, animationURL, statsURL, outURL;
    
    for(var i=0; i<data.resources.length; i++) 
    {
      // for current version I only list the three input files
      if(data.resources[i].resource_type == 'control')
      {
        controlURL = data.resources[i].resource_url;
        //alert(controlURL);
      }
      else if(data.resources[i].resource_type == 'data')
      {
        dataURL = data.resources[i].resource_url;
      }
      else if(data.resources[i].resource_type == 'param')
      {
        paramURL = data.resources[i].resource_url;
      }
      else if(data.resources[i].resource_type == 'animation')
      {
        animationURL = data.resources[i].resource_url;
      }
      else if(data.resources[i].resource_type == 'statsvar')
      {
        statsURL = data.resources[i].resource_url;
      }
      else if(data.resources[i].resource_type == 'output')
      {
        outURL = data.resources[i].resource_url;
      }
    }

    //fire a jax call from here

    $.ajax({
            type : "GET",
            url : "/download_Model_Data",
            data:{
                controlURL: controlURL,
                dataURL:dataURL,
                paramURL:paramURL,
                animationURL:animationURL,
                statsURL:statsURL,
                outURL:outURL,

                model_Id:data.id,
                model_type:data.model_name,
                model_desc:data.description,
                model_title:data.title
            },
            dataType: 'json',
            contentType: 'application/json',
            success: function(result) {
                var modeluuid_vwp = result.modeluuid_vwp;
                var pushed_time = result.pushed_time;
                var model_Id = result.model_Id;

                var param_code = result.param_file_status_code;
                var data_code = result.data_file_status_code;
                var control_code = result.control_file_status_code;
                var statvar_code = result.statvar_file_status_code;
                var output_code = result.output_file_status_code;
                var animation_code = result.animation_file_status_code;


                if(param_code==200 && data_code==200 && control_code==200 && statvar_code==200 && output_code==200 && (animation_code==200 || animation_code==null)){
                    //All upload successful
                            label_vwpID = "#vwpID-".concat(model_Id)
                            label_pushID = "#pushID-".concat(model_Id)
                           
                            $(label_vwpID).text(modeluuid_vwp);
                            $(label_pushID).text(pushed_time);
                                       
                            buttonId = model_Id.concat('|').concat(modeluuid_vwp)
                            $(button).attr('id',buttonId);
                            $(button).text('Remove-VWP');
                            $(button).removeClass('btn-info').addClass('btn-danger');          
                }else{
                         //if any error in uploading any of the files - remove the modelVWPid from GSTORE
                         remove_vwp_push(model_Id,modeluuid_vwp, button);

                         $('#error-info').addClass('alert alert-danger');
                         $('#error-info').append('Sorry, We encountered below errors while pushing the model run...Please try later');
                         if(param_code!=200){
                            $('#error-info').append('Failed - Uploading parameter file');
                         }
                         if(control_code!=200){
                            $('#error-info').append('Failed - Uploading control file');
                         }
                         if(data_code!=200){
                            $('#error-info').append('Failed - Uploading data file');
                         }

                         if(statvar_code!=200){
                            $('#error-info').append('Failed - Uploading statvar file');
                         }
                         if(output_code!=200){
                            $('#error-info').append('Failed - Uploading output file');
                         }
                         if(animation_code!=null && animation_code!=200){
                            $('#error-info').append('Failed - Uploading data file');
                         }
                }
            }
    });
  }
  

  
  function remove_vwp_push(modelRunID,vwpModelId, button){
   $.ajax({
      type: "GET",
      url: '/remove_vwp_push',
      data:{ 
        vwpModelId:vwpModelId,
        modelRunID:modelRunID
      },
      dataType: 'json',
      contentType: "application/json; charset=utf-8",
      success: function(data) {
          // success handler
          var jsonData = JSON.parse(data); 
          if (jsonData ==true){
                buttonId = modelRunID.concat('|')
                $(button).attr('id',buttonId);
                $(button).text('Push-VWP');
                $(button).removeClass('btn-info');
                $(button).removeClass('btn-danger').addClass('btn-success');


                label_vwpID = "#vwpID-".concat(modelRunID)
                label_pushID = "#pushID-".concat(modelRunID)

                $(label_vwpID).text('');
                $(label_pushID).text('');
          }
      }
    });
  
  }
