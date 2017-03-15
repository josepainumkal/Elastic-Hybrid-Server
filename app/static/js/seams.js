var totalAmount = 0;
function slider_change(input_value){
  
  // $('#slide_p').text("Current budget is: "+input_value.toString());
  $('#lb_budget').text(input_value.toString());
  $('#lb_rate').text($('#rate').val());
  $('#lb_tavg').text($('#tavg').val());
  $('#lb_duration').text($('#duration').val());


    var totalAmount = parseFloat(input_value);
    $('#lb_amount').text(totalAmount);

    var instance_rate = parseFloat($('#rate').val());
    var tavg_modelrun_secs = parseFloat($('#tavg').val());
    // var budget_period_min = parseFloat($('#duration').val());
    var budget_period_hr = parseFloat($('#duration').val());


    // var budget_period_hr = parseFloat(budget_period_min/60);
    var tavg_modelrun_hr = parseFloat(tavg_modelrun_secs/3600);
    var tavg_modelrun_mins = parseFloat(tavg_modelrun_secs/60);

    
    var total_rented_modelruns_allowed = parseInt(totalAmount/(instance_rate*tavg_modelrun_hr));
    var time_interval_hr = parseFloat(budget_period_hr/total_rented_modelruns_allowed);
    var time_interval_min = parseFloat(time_interval_hr*60);
    var time_interval_sec = parseFloat(time_interval_min*60);


    var tavg_for_owned = parseFloat(34);
    var mu_own = parseFloat(1/tavg_modelrun_hr);
    var mu_rent =totalAmount/(instance_rate*tavg_modelrun_hr)
    var mu = parseFloat(mu_own+mu_rent);
    var lamda = parseFloat($('#lamda').val());


    var rho = parseFloat(lamda*1.0/mu);
    var length_system =parseFloat(rho/(1-rho));
    var length_queue = length_system-rho;

    var waiting_queue = parseFloat(length_queue/lamda);
    var waiting_system = parseFloat(length_system/lamda);

    length_queue = length_queue/(budget_period_hr*60.0);



    total_rented_modelruns_allowed = parseInt(total_rented_modelruns_allowed);
    
    $('#lb_totalmodelruns').text(total_rented_modelruns_allowed.toFixed(2));
    $('#lb_modelruns_rented').text(mu_rent.toFixed(2));
    $('#lb_modelruns_owned').text(mu_own.toFixed(2));
    $('#lb_wq').text(waiting_queue.toFixed(2));
    $('#lb_interval').text(time_interval_sec.toFixed(2));
    $('#lb_ql').text(length_queue.toFixed(2));
    $('#lb_mu').text(mu.toFixed(2));

    if(lamda>=mu){
      $('#lamdaError').show();
    }else{
      $('#lamdaError').hide();
    }

}

$(document).ready(function(){

  get_alert_email_list();
  get_email_settings();

  

  $(document).on('click', '#showInfoId', function () {

    $('#lb_budget').text($('#totalamount').val());
    $('#lb_amount').text($('#totalamount').val());
    $('#lb_rate').text($('#rate').val());
    $('#lb_tavg').text($('#tavg').val());
    $('#lb_duration').text($('#duration').val());

    var totalAmount = parseFloat($('#totalamount').val());
    var instance_rate = parseFloat($('#rate').val());
    var tavg_modelrun_secs = parseFloat($('#tavg').val());
    // var budget_period_min = parseFloat($('#duration').val());
    var budget_period_hr = parseFloat($('#duration').val());


    // var budget_period_hr = parseFloat(budget_period_min/60);
    var tavg_modelrun_hr = parseFloat(tavg_modelrun_secs/3600);
    var tavg_modelrun_mins = parseFloat(tavg_modelrun_secs/60);

    
    var total_rented_modelruns_allowed = parseInt(totalAmount/(instance_rate*tavg_modelrun_hr));
    var time_interval_hr = parseFloat(budget_period_hr/total_rented_modelruns_allowed);
    var time_interval_min = parseFloat(time_interval_hr*60);
    var time_interval_sec = parseFloat(time_interval_min*60);


    var tavg_for_owned = parseFloat(34);
    var mu_own = parseFloat(budget_period_hr/tavg_modelrun_hr);
    var mu_rent =totalAmount/(instance_rate*tavg_modelrun_hr)
    var mu = parseFloat(mu_own+mu_rent);
    var lamda = parseFloat($('#lamda').val());


    var rho = parseFloat(lamda*1.0/mu);
    var length_system =parseFloat(rho/(1-rho));
    var length_queue = length_system-rho;

    var waiting_queue = parseFloat(length_queue/lamda);
    var waiting_system = parseFloat(length_system/lamda);

    length_queue = length_queue/(budget_period_hr*60.0);



    total_rented_modelruns_allowed = parseInt(total_rented_modelruns_allowed);

    $('#lb_totalmodelruns').text(total_rented_modelruns_allowed.toFixed(2));
    $('#lb_modelruns_rented').text(mu_rent.toFixed(2));
    $('#lb_modelruns_owned').text(mu_own.toFixed(2));
    $('#lb_wq').text(waiting_queue.toFixed(2));
    $('#lb_interval').text(time_interval_sec.toFixed(2));
    $('#lb_ql').text(length_queue.toFixed(2));
    $('#lb_mu').text(mu.toFixed(2));

    if(lamda>=mu){
      $('#lamdaError').show();
    }else{
      $('#lamdaError').hide();
    }

  });

  $(document).on("click", "#activateId" , function() {
    $('#activate_box').show();
    $.ajax({
            type: "POST",
            url: "/seams_activate",
            data: $('#activate_seams').serialize(),
            success: function(response){

            },
            error: function(error) {
            }
    });
  });


  $(document).on('click', '#feedbackSubmitId', function () {
        // console.log($('input[name=q1]:checked').val());
        // console.log($('input[name=q2]:checked').val());
        // console.log($('input[name=q3]:checked').val());
        // console.log($('input[name=q4]:checked').val());

        $.ajax({
          type: "POST",
          url: "/survey_submit",
          data: $('#feedback_form').serialize(),
          success: function(response){
                $('#survey_submit_notification_box').show();    
                $('input[type=radio]').prop('checked', false);
          },
          error: function(error) {
          }
       });



  });

    $(document).on("click", "#btn_addemail" , function() {
    $.ajax({
            type: "POST",
            url: "/add_email",
            data: $('#insert_Email').serialize(),
            success: function(response){

                  get_alert_email_list();
                  $('#addemail').val('');    
             


            },
            error: function(error) {
            }
    });
  });


  $(document).on("click", "#btn_delemail" , function() {
    $.ajax({
            type: "POST",
            url: "/del_email",
            data: $('#remove_Email').serialize(),
            success: function(response){
                  get_alert_email_list();
                  $('#delemail').val('');    
            },
            error: function(error) {
            }
    });
  });

    $(document).on("click", "#btn_modifytime" , function() {
    $.ajax({
            type: "POST",
            url: "/modify_email_timeinterval",
            data: $('#modify_time_interval').serialize(),
            success: function(response){
                  get_email_settings();
                  $('#new_timeinterval').val('');    
            },
            error: function(error) {
            }
    });
  });

        $(document).on("click", "#btn_thval" , function() {
    $.ajax({
            type: "POST",
            url: "/modify_threshold_score",
            data: $('#modify_th_value').serialize(),
            success: function(response){
                   get_email_settings();
                  $('#newthval').val('');    
            },
            error: function(error) {
            }
    });
  });
});



function get_email_settings(){
   $.ajax({
      type: "GET",
      url: '/emailSettings',
      // contentType: "application/json; charset=utf-8",
      dataType: 'json',
      contentType: 'application/json',
      success: function(data) {
          // var jsonData = JSON.parse(data); 
          $('#e_interval').text(data.email_interval);  
          $('#e_threshold').text(data.fd_threshold);  
          $('#e_fd_score').text(parseFloat(data.fd_score).toFixed(2));  

      }
    });

}




function get_alert_email_list(){
   $.ajax({
      type: "GET",
      url: '/alert_email_list',
      // contentType: "application/json; charset=utf-8",
      dataType: 'json',
      contentType: 'application/json',
      success: function(data) {
          // var jsonData = JSON.parse(data); 
          list_alert_emailIds(data);
      }
    });

}

function list_alert_emailIds(data){
  $('#alertEmailList').text('');

  for(var i = 0; i<data.length; i++){

     $('#alertEmailList').append(data[i]+'<br>');
  }
}