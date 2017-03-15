
 google.charts.load('current', {'packages':['corechart']});


$(document).ready(function () {
  //your code here
  get_user_feedbacks();

});




function drawChart(param) {

  // Create the data table.
  var data = new google.visualization.DataTable();
      data.addColumn('string', 'Topping');
      data.addColumn('number', 'Slices');
      data.addRows([
      [param, 3],
      ['Onions', 1],
      ['Olives', 1],
      ['Zucchini', 1],
      ['Pepperoni', 2]
      ]);

      // Set chart options
      var options = {'title':'How Much Pizza I Ate Last Night',
                   'width':450,
                   'height':300};

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.BarChart (document.getElementById('chart_div1'));
      chart.draw(data, options);
}



function get_user_feedbacks(){
   $.ajax({
      type: "GET",
      url: '/get_user_feedbacks',
      // contentType: "application/json; charset=utf-8",
      dataType: 'json',
      contentType: 'application/json',
      success: function(resp) {
          // var jsonData = JSON.parse(resp); 
          google.charts.setOnLoadCallback(function() {
                display_user_feedbacks(resp);
          });
          // display_user_feedbacks(resp);
      }
    });
}


function display_user_feedbacks(resp){
  
  google.charts.load('current', {'packages':['corechart']});

  for(var i = 0; i<resp.length; i++){
      title = resp[i].title;
      option1 =  resp[i].option1;
      option2 =  resp[i].option2;
      option3 =  resp[i].option3;
      option1_count =  resp[i].option1_count;
      option2_count =  resp[i].option2_count;
      option3_count =  resp[i].option3_count;

      var data = new google.visualization.DataTable();
      data.addColumn('string', 'option_desc');
      data.addColumn('number', 'Count');

      // data.addRows([[option1, option1_count], [option2, option2_count], [option3, option3_count]]);

      data.addRows([
      [option1, parseInt(option1_count)],
      [option2, parseInt(option2_count)],
      [option3, parseInt(option3_count)]
      ]);


      var options = {'title':title,'width':450,'height':300};

      div_id='chart_div'+(i+1);
      bar_id='bar'+(i+1);

      var chart = new google.visualization.ColumnChart (document.getElementById(div_id));
      chart.draw(data, options);


      // var chart_div = document.getElementById(div_id);
      // var chart = new google.visualization.ColumnChart(chart_div);

      // // Wait for the chart to finish drawing before calling the getImageURI() method.
      // google.visualization.events.addListener(chart, 'ready', function () {
      //   chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
      //   // console.log(chart.getImageURI());
      //   $('#'+bar_id).val(chart.getImageURI());
      // });

      // chart.draw(data, options);
  }  
}
