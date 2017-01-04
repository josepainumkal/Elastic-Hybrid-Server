  $( function() {
    // $( "#slider" ).slider();

  } );


 $('#foo').slider().on('slide', function(ev){
            $('#bar').val(ev.value);
        });

$(document).on('click', '#submitbtn', function () {

  // alert('hello');

  // var totalAmount = $('#totalamount').val();

  $('#lb_amount').text($('#totalamount').val());
  $('#lb_rate').text($('#rate').val());
  $('#lb_tavg').text($('#tavg').val());
  $('#lb_duration').text($('#duration').val());


  var totalAmount = parseFloat($('#totalamount').val());
  var rate = parseFloat($('#rate').val());
  var tavg = parseFloat($('#tavg').val());
  var duration_hrs = parseFloat($('#duration').val());


  tavg_modelrun_mins = tavg/60.0
  total_rented_modelruns_allowed = totalAmount/(tavg_modelrun_mins*rate)
  timeInterval_secs = ((duration_hrs * 60)/total_rented_modelruns_allowed) * 60.0

  mu_owned = 60.0/tavg
  mu_rented = 60.0/timeInterval_secs
  total_mu = mu_owned + mu_rented
  lamda = total_mu-1

  rho = parseFloat(lamda*1.0/total_mu)
  length_system =parseFloat(rho/(1-rho))
  length_queue = length_system-rho



  waiting_queue = parseFloat(length_queue*1.0/lamda)
  waiting_system = parseFloat(length_system/lamda)



  $('#lb_totalmodelruns').text(total_rented_modelruns_allowed);
  $('#lb_modelruns_rented').text(mu_rented);
  $('#lb_modelruns_owned').text(mu_owned);
  $('#lb_wq').text(waiting_queue);
  $('#lb_interval').text(timeInterval_secs);

  $('.span2').slider()




//   total_money = float(100)
// container_rate_per_min = float(1)
// tavg_modelrun_secs = float(10)
// tavg_modelrun_mins = float(tavg_modelrun_secs/60)
// total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
// # time interval calculated for one hour. i.e, we are distributing total_rented_modelruns_allowed among the one hour
// time_interval = float(60.0/total_rented_modelruns_allowed)
// time_interval=time_interval*60

// print '\nTotal Money: ', total_money, '$'
// print 'Rate of Container: ', container_rate_per_min,' $/min'
// print 'Average time for modelrun : ', tavg_modelrun_secs,' sec'
// print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
// print 'Calculated time interval  : ', time_interval,' sec'


//                           <strong>Total Amount ($):</strong>&nbsp;&nbsp;<span id="lb_amount"></span><br>
//                                          <strong>Container Rate($/min):</strong>&nbsp;&nbsp;<span id="lb_rate"></span><br>
//                                          <strong>Average Time (sec):</strong>&nbsp;&nbsp;<span id="lb_tavg"></span><br>
//                                          <strong>Duration (No of Hours.):</strong>&nbsp;&nbsp;<span id="lb_duration"></span><br><br>
                                        
//                                          <strong>Total Model Runs :</strong>&nbsp;&nbsp;<span id="lb_totalmodelruns"></span><br>
//                                          <strong>Model runs served by rented workers (1 min) :</strong>&nbsp;&nbsp;<span id="lb_modelruns_rented"></span><br>
//                                          <strong>Model runs served by owned workers (1 min) :</strong>&nbsp;&nbsp;<span id="lb_modelruns_owned"></span><br>
//                                          <strong>Expected Waiting Time in Queue :</strong>&nbsp;&nbsp;<span id="lb_wq"></span><br>



   // var currentCount = $('.repeat-parameter').length;
   // var newCount = currentCount + 1;
   // var lastRepeatingGroup = $('.repeat-parameter').last();
   // var template = $('.repeat-parameter').first();
   // // var template = template0;
   // var newSection = template.clone();

   // newSection.attr('id',newCount);
   // newSection.find(".highValue").remove();
  
   // newSection.insertAfter(lastRepeatingGroup).hide().slideDown(250);

   // newSection.find("select").each(function (index, input) {
   //      var i = $(this).attr('id');
   //      $(this).attr('id', i.split('1')[0] + newCount);
   //      $(this).attr('name', i.split('1')[0] + newCount);
   // });

   // newSection.find("input").each(function (index, input) {
   //      var i = $(this).attr('id');
   //      $(this).attr('id', i.split('1')[0] + newCount);
   //      $(this).attr('name', i.split('1')[0] + newCount);
   // });


   // if(newCount >1){
   // 	   $('#deleteParam').show();
   // }
   // $('#totalParams').val(newCount);
   // return false;
});